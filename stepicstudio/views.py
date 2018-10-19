import itertools
import copy
import re
from wsgiref.util import FileWrapper

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.template import RequestContext

from stepicstudio.forms import LessonForm, StepForm
from stepicstudio.postprocessing import start_subtep_montage, start_step_montage, start_lesson_montage
from stepicstudio.video_recorders.action import *
from stepicstudio.file_system_utils.action import search_as_files_and_update_info, rename_element_on_disk
from stepicstudio.utils.utils import *
from stepicstudio.statistic import add_stat_info

logger = logging.getLogger('stepicstudio.views')


def can_edit_page(view_function):
    def process_request(*args, **kwargs):
        access = test_access(args[0].user.id, list(filter(None, args[0].path.split('/'))))
        if not access:
            return HttpResponseRedirect(reverse('stepicstudio.views.login'))
        else:
            return view_function(*args, **kwargs)

    return process_request


def cant_edit_course(user_id, course_id):
    courses_from_user_id = Course.objects.all().filter(editors=user_id)
    course = Course.objects.all().filter(id=course_id)[0]
    if course in courses_from_user_id:
        return False
    else:
        return True


# TODO: Add substep checks
def test_access(user_id, path_list):
    if COURSE_ULR_NAME in path_list:
        course_id = path_list[path_list.index(COURSE_ULR_NAME) + 1]
    else:
        course_id = None
    if LESSON_URL_NAME in path_list:
        lesson_id = path_list[path_list.index(LESSON_URL_NAME) + 1]
    else:
        lesson_id = None
    if STEP_URL_NAME in path_list:
        step_id = path_list[path_list.index(STEP_URL_NAME) + 1]
    else:
        step_id = None
    if path_list[0] == COURSE_ULR_NAME and not cant_edit_course(user_id, course_id):
        if lesson_id and not (str(Lesson.objects.all().get(id=lesson_id).from_course) == str(course_id)):
            return False
        if step_id and not (int(Step.objects.all().get(id=step_id).from_lesson) == int(lesson_id)):
            return False
        return True
    else:
        return False


def index(request):
    if request.user.username:
        return HttpResponseRedirect('/loggedin/')
    return HttpResponseRedirect(reverse('stepicstudio.views.login'))


def login(request, **kwargs):
    c = {}
    if 'error' in kwargs.keys():
        c.update({'error': True})
    c.update(csrf(request))
    return render_to_response('login.html', c, context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('stepicstudio.views.login'))


@login_required(login_url='/login/')
def get_user_courses(request):
    args = {'full_name': request.user.username,
            'Courses': Course.objects.all().filter(editors=request.user.id),
            }
    args.update({'Recording': camera_curr_status})
    return render_to_response('courses.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def get_course_page(request, course_id):
    lesson_list = [l for l in Lesson.objects.all().filter(from_course=course_id)]
    lesson_list.sort(key=lambda lesson: lesson.position)
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'Lessons': lesson_list,
            }
    args.update({'Recording': camera_curr_status})
    return render_to_response('course_view.html', args, context_instance=RequestContext(request))


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        say_hello = UserProfile.objects.get(user=user).is_ready_to_show_hello_screen
        auth.login(request, user)
        if say_hello:
            say_hello = '?message=hi'
        else:
            say_hello = ''
        return HttpResponseRedirect('/loggedin/' + say_hello)
    else:
        return login(request, error=True)


def loggedin(request):
    if request.user.is_authenticated():
        say_hello = bool(request.GET.get('message'))
        return render_to_response('loggedin.html', {'full_name': request.user.username,
                                                    'Courses': Course.objects.all(),
                                                    'say_hello': say_hello,
                                                    }
                                  , context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('stepicstudio.views.login'))


# TODO: Implement correctly !!! REDECORATE WITH CAN_EDIT_PAGE
@login_required(login_url='/login/')
def add_lesson(request):
    if request.method == 'GET':
        if request.META.get('HTTP_REFERER'):
            try:
                url_arr = (request.META.get('HTTP_REFERER')).split('/')
                _id = url_arr[url_arr.index('course') + 1]
                form = LessonForm(userId=request.user.id, from_course=_id)
            except:
                return error500_handler(request)
        else:
            raise Http404
    elif request.method == 'POST':
        form = LessonForm(request.POST, userId=request.user.id)
        if form.is_valid():
            from_course = form.data['from_courseName']
            saved_lesson = form.lesson_save()
            last_saved = Lesson.objects.get(id=saved_lesson.pk)
            last_saved.from_course = from_course
            last_saved.save()
            return HttpResponseRedirect('/course/' + from_course + '/')
    else:
        raise Http404

    args = {'full_name': request.user.username}
    args.update(csrf(request))
    args.update({'Recording': camera_curr_status})
    args['form'] = form
    return render_to_response('create_lesson.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def show_lesson(request, course_id, lesson_id):
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Steps': Step.objects.all().filter(from_lesson=lesson_id).order_by('position'),

            }
    args.update({'Recording': camera_curr_status})
    return render_to_response('lesson_view.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def delete_lesson(request, course_id, lesson_id):
    lesson_obj = Lesson.objects.get(id=lesson_id)
    redirect_to_course_page = request.path.split('/')
    if not delete_files_associated(redirect_to_course_page):
        raise Exception('Cant delete files')
    for step in Step.objects.all().filter(from_lesson=lesson_id):
        for substep in SubStep.objects.all().filter(from_step=step.pk):
            substep.delete()
        step.delete()
    lesson_obj.delete()
    return HttpResponseRedirect('/' + '/'.join(redirect_to_course_page[1:3]) + '/')


# IMPLEMENT CORRECTLY
@login_required(login_url='/login/')
@can_edit_page
def add_step(request, course_id, lesson_id):
    if request.POST:
        form = StepForm(request.user.id, lesson_id, request.POST)
        if form.is_valid():
            from_lesson = form.data['from_lessonId']
            saved_step = form.step_save()
            last_saved = Step.objects.get(id=saved_step.pk)
            last_saved.from_lesson = from_lesson
            last_saved.save()
            return HttpResponseRedirect('/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME +
                                        '/' + from_lesson + '/')
    else:
        form = StepForm(request.user.id, lesson_id)

    args = {'full_name': request.user.username,
            'postUrl': '/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME
                       + '/' + lesson_id + '/add_step/',
            }
    args.update({'Recording': camera_curr_status})
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('create_step.html', args, context_instance=RequestContext(request))


def to_custom_name(substep_name, user_name_template):
    m = re.search(r'Step(\d+)from(\d+)', substep_name)
    ss_id, s_id = (m.group(1), m.group(2))
    tmp = re.sub(r'(\$id)', re.escape(ss_id), user_name_template)
    fin = re.sub(r'(\$stepid)', re.escape(s_id), tmp)
    return fin


@login_required(login_url='/login/')
@can_edit_page
def show_step(request, course_id, lesson_id, step_id):
    step_obj = Step.objects.get(id=step_id)
    if request.POST and request.is_ajax():
        user_action = dict(request.POST.lists())['action'][0]
        if user_action == 'start':
            start_status = start_new_step_recording(request, course_id, lesson_id, step_id)
            if start_status.status is ExecutionStatus.SUCCESS:
                step_obj.is_fresh = False
                return HttpResponse('Ok')
            elif start_status.status is ExecutionStatus.FIXABLE_ERROR:
                return HttpResponseServerError(start_status.message)
            elif start_status.status is ExecutionStatus.FATAL_ERROR:
                return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')
        elif user_action == 'stop':
            stop_status = stop_cam_recording()
            if stop_status:
                return HttpResponse('Ok')
            else:
                return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')

    all_substeps = SubStep.objects.all().filter(from_step=step_id).order_by('-start_time')
    summ_time = update_time_records(all_substeps)
    step_obj.is_fresh = True
    step_obj.duration += summ_time
    step_obj.save()
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().get(id=course_id),
            'Lesson': Lesson.objects.all().get(id=lesson_id),
            'Step': Step.objects.get(id=step_id),
            'postUrl': request.path,
            'SubSteps': all_substeps,
            'tmpl_name': UserProfile.objects.get(user=request.user.id).substep_template,

            }
    args.update({'Recording': camera_curr_status})
    args.update(csrf(request))
    return render_to_response('step_view.html', args, context_instance=RequestContext(request))


# TODO: request.META is BAD! replace for AJAX requests!
@login_required(login_url='/login')
def notes(request, step_id):
    if request.POST:
        step_obj = Step.objects.get(id=step_id)
        step_obj.text_data = dict(request.POST.lists())['note'][0]
        step_obj.save()
    args = {}
    args.update(csrf(request))
    return HttpResponseRedirect(request.META['HTTP_REFERER'], args)


# TODO: user_id probably dont needed
@login_required(login_url='/login')
def update_substep_tmpl(request):
    if request.POST:
        try:
            new_name = (dict(request.POST.lists())['template'][0])
            if '$id' not in new_name and '$stepid' not in new_name:
                return HttpResponseBadRequest('Template should include "$id" and "$stepid" elements.')
            profile = UserProfile.objects.get(user=request.user.id)
            profile.substep_template = new_name
            profile.save()
        except Exception:
            logger.exception('Error while update substep template')
            return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')
    args = {}
    args.update(csrf(request))
    return HttpResponse('Ok')


# TODO: TOKEN at POSTrequest to statistic server is insecure
# TODO: Off by one error here with substep naming need fix ( no Step1From** will be created)
@login_required(login_url='/login/')
def start_new_step_recording(request, course_id, lesson_id, step_id) -> InternalOperationResult:
    substep = SubStep()
    substep.from_step = step_id
    substep_index = SubStep.objects.filter(from_step=step_id).count() + 1
    substep.name = 'Step' + str(substep_index) + 'from' + str(substep.from_step)
    while SubStep.objects.filter(name=substep.name).count():
        substep_index += 1
        substep.name = 'Step' + str(substep_index) + 'from' + str(substep.from_step)
    substep.save()
    post_url = '/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME + '/' + lesson_id + '/' + \
               STEP_URL_NAME + '/' + step_id + '/'
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'postUrl': post_url,
            'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Step': Step.objects.all().filter(id=step_id)[0],
            'SubSteps': SubStep.objects.all().filter(from_step=step_id),
            'currSubStep': SubStep.objects.get(id=substep.pk),
            }
    args.update(csrf(request))
    recording_status = start_recording(user_id=request.user.id,
                                       user_profile=UserProfile.objects.get(user=request.user.id),
                                       data=args)
    if recording_status.status is ExecutionStatus.SUCCESS:
        args.update({'Recording': True})
        args.update({'StartTime': CameraStatus.objects.get(id='1').start_time / 1000})
    else:
        substep.delete()
    return recording_status


@login_required(login_url='/login')
def montage(request, substep_id):
    if not request.is_ajax():
        raise Http404

    start_subtep_montage(substep_id)
    return HttpResponse('Ok')


def step_montage(request, step_id):
    if not request.is_ajax():
        raise Http404

    start_step_montage(step_id)
    return HttpResponse('Ok')


def lesson_montage(request, lesson_id):
    if not request.is_ajax():
        raise Http404

    start_lesson_montage(lesson_id)
    return HttpResponse('Ok')


@login_required(login_url='/login')
def substep_status(request, substep_id):
    if not request.is_ajax():
        raise Http404
    try:
        substep = SubStep.objects.all().get(id=substep_id)
        is_locked = substep.is_locked
        is_automontage_exists = substep.automontage_exist

        args = {'islocked': is_locked,
                'isexists': is_automontage_exists}

        return JsonResponse(args)
    except:
        return HttpResponseServerError()


@login_required(login_url='/login')
def recording_page(request, course_id, lesson_id, step_id):
    post_url = '/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME + '/' + lesson_id + '/' + \
               STEP_URL_NAME + '/' + step_id + '/'
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'postUrl': post_url,
            'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Step': Step.objects.all().filter(id=step_id)[0],
            'SubSteps': SubStep.objects.all().filter(from_step=step_id),

            }
    args.update({'Recording': camera_curr_status})
    return render_to_response('step_view.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login')
def stop_all_recording(request):
    stop_cam_recording()
    return HttpResponse('Ok')


@login_required(login_url='/login')
def stop_recording(request, course_id, lesson_id, step_id):
    post_url = '/' + COURSE_ULR_NAME + '/' + str(course_id) + '/' + LESSON_URL_NAME + '/' + str(lesson_id) + '/' + \
               STEP_URL_NAME + '/' + str(step_id) + '/'
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'postUrl': post_url, 'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Step': Step.objects.all().filter(id=step_id)[0],
            'SubSteps': SubStep.objects.all().filter(from_step=step_id)}
    args.update(csrf(request))
    stop_cam_status = stop_cam_recording()
    args.update({'Recording': camera_curr_status})
    last_substep_time = SubStep.objects.all().filter(from_step=step_id) \
        .aggregate(Max('start_time'))['start_time__max']
    recorded_substep = SubStep.objects.all().filter(start_time=last_substep_time)[0]
    add_stat_info(recorded_substep.id)
    return stop_cam_status


@login_required(login_url='/login/')
@can_edit_page
def remove_substep(request, course_id, lesson_id, step_id, substep_id):
    substep = SubStep.objects.get(id=substep_id)
    post_url = '/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME + '/' + lesson_id + '/' + \
               STEP_URL_NAME + '/' + step_id + '/'
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Step': Step.objects.all().filter(id=step_id)[0],
            'postUrl': post_url,
            'SubSteps': SubStep.objects.all().filter(from_step=step_id),
            'currSubStep': substep,
            }

    delete_substep_files(user_id=request.user.id,
                         user_profile=UserProfile.objects.get(user=request.user.id),
                         data=args)
    substep.delete()
    return HttpResponseRedirect(post_url)


@login_required(login_url='/login/')
@can_edit_page
def delete_step(request, course_id, lesson_id, step_id):
    step = Step.objects.all().get(id=step_id)
    post_url = '/' + COURSE_ULR_NAME + '/' + course_id + '/' + LESSON_URL_NAME + '/' + lesson_id + '/'
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().filter(id=course_id)[0],
            'Lesson': Lesson.objects.all().filter(id=lesson_id)[0],
            'Step': Step.objects.all().filter(id=step_id)[0],
            'postUrl': post_url,
            'SubSteps': SubStep.objects.all().filter(from_step=step_id),
            }
    substeps = SubStep.objects.all().filter(from_step=step_id)
    step_deleted = delete_step_files(user_id=request.user.id,
                                     user_profile=UserProfile.objects.get(user=request.user.id), data=args)
    if step_deleted:
        for substep in substeps:
            substep.delete()
        step.delete()
    return HttpResponseRedirect(post_url)


@login_required(login_url='/login/')
def user_profile(request):
    return render_to_response('UserProfile.html',
                              {'full_name': request.user.username,
                               'settings': UserProfile.objects.get(user_id=request.user.id)},
                              context_instance=RequestContext(request))


# TODO: Refactor
def reorder_elements(request):
    if request.POST and request.is_ajax():
        args = url_to_args(request.META['HTTP_REFERER'])
        args.update({'user_profile': UserProfile.objects.get(user=request.user.id)})
        if request.POST.get('type') == 'lesson' or request.POST.get('type') == 'step':
            neworder = request.POST.getlist('ids[]')
            for i in range(len(neworder)):
                id = neworder[i]
                if id == '':
                    break
                if request.POST.get('type') == 'lesson':
                    l = Lesson.objects.get(id=id)
                else:
                    l = Step.objects.get(id=id)
                l.position = i
                l.save()
        return HttpResponse('Ok')

    else:
        return Http404


@login_required(login_url='/login/')
@can_edit_page
def show_course_struct(request, course_id):
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().get(id=course_id),
            }
    args.update({'user_profile': UserProfile.objects.get(user=request.user.id)})
    args.update({'Recording': camera_curr_status})
    all_lessons = Lesson.objects.all().filter(from_course=course_id)
    args.update({'all_course_lessons': all_lessons})
    all_steps = ()
    for l in all_lessons:
        steps = Step.objects.all().filter(from_lesson=l.pk)
        all_steps = itertools.chain(all_steps, steps)
    all_steps = list(all_steps)
    args.update({'all_steps': all_steps})
    args = search_as_files_and_update_info(args)
    args.update(csrf(request))
    return render_to_response('course_struct.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def view_stat(request, course_id):
    args = {'full_name': request.user.username,
            'Course': Course.objects.all().get(id=course_id),
            }
    return render_to_response('stat.html', args, context_instance=RequestContext(request))


# TODO: This function is unsafe, its possible to watch other users files
@login_required(login_url='/login/')
def video_view(request, substep_id):
    try:
        fs_client = FileSystemClient()
        substep = SubStep.objects.all().get(id=substep_id)
        path = substep.os_path
        base_path = os.path.splitext(path)[0]

        if fs_client.is_file_valid(base_path + '.mp4'):
            path_to_show = base_path + '.mp4'
            file = FileWrapper(open(path_to_show, 'rb'))
            response = HttpResponse(file, content_type='video/mp4')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              substep.name + '_' + \
                                              os.path.splitext(SUBSTEP_PROFESSOR)[0] + '.mp4'
        else:
            file = FileWrapper(open(path, 'rb'))
            response = HttpResponse(file, content_type='video/TS')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              substep.name + '_' + \
                                              SUBSTEP_PROFESSOR

        return response
    except FileNotFoundError as e:
        logger.warning('Missing file: %s', str(e))
        return error_description(request, 'File is missed.')
    except Exception as e:
        return error500_handler(request)


# TODO: hotfix here is bad =(
@login_required(login_url='/login/')
def video_screen_view(request, substep_id):
    try:
        fs_client = FileSystemClient()
        substep = SubStep.objects.all().get(id=substep_id)
        path = '/'.join((list(filter(None, substep.os_path.split('/'))))[:-1]) + '/' + substep.name + SUBSTEP_SCREEN
        base_path = os.path.splitext(path)[0]

        if fs_client.is_file_valid(base_path + '.mp4'):
            path_to_show = base_path + '.mp4'
            file = FileWrapper(open(path_to_show, 'rb'))
            response = HttpResponse(file, content_type='video/mp4')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              substep.name + '_' + \
                                              os.path.splitext(SUBSTEP_SCREEN)[0] + '.mp4'
        else:
            file = FileWrapper(open(path, 'rb'))
            response = HttpResponse(file, content_type='video/TS')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              substep.name + '_' + \
                                              SUBSTEP_SCREEN

        return response
    except FileNotFoundError as e:
        logger.warning('Missed file: %s', str(e))
        return error_description(request, 'File is missed.')
    except Exception:
        return error500_handler(request)


def show_montage(request, substep_id):
    try:
        substep = SubStep.objects.all().get(id=substep_id)
        path = substep.os_automontage_file
        file = FileWrapper(open(path, 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = 'inline; filename=' + substep.name + RAW_MONTAGE_LABEL
        return response
    except FileNotFoundError as e:
        logger.warning('Missed file: %s', str(e))
        return error_description(request, 'File is missed.')
    except Exception:
        return error500_handler(request)


def rename_elem(request):
    if request.POST and request.is_ajax():
        rest_data = dict(request.POST.lists())
        if 'step' in rest_data['type'] or 'lesson' in rest_data['type']:
            if 'step' in rest_data['type']:
                obj_to_rename = Step.objects.all().get(id=rest_data['id'][0])
            else:
                obj_to_rename = Lesson.objects.all().get(id=rest_data['id'][0])

            logger.debug('Renaming: %s', obj_to_rename.os_path)
            tmp_step = copy.copy(obj_to_rename)
            tmp_step.name = rest_data['name_new'][0]

            if not camera_curr_status():
                rename_status = rename_element_on_disk(obj_to_rename, tmp_step)
                if rename_status.status is ExecutionStatus.SUCCESS:
                    obj_to_rename.delete()
                    tmp_step.save()
                    return HttpResponse('Ok')
                elif rename_status.status is ExecutionStatus.FIXABLE_ERROR:
                    return HttpResponseServerError(rename_status.message)
                elif rename_status.status is ExecutionStatus.FATAL_ERROR:
                    return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')
            else:
                return Http404
        else:
            return Http404
    else:
        return Http404


def clear_all_locked_substeps(request):
    all_locked = SubStep.objects.all().filter(is_locked=True)
    for ss in all_locked:
        ss.is_locked = False
        ss.save()
    return render_to_response('UserProfile.html',
                              {'full_name': request.user.username,
                               'settings': UserProfile.objects.get(user_id=request.user.id)},
                              context_instance=RequestContext(request))


def generate_notes_page(request, course_id):
    lessons = Lesson.objects.all().filter(from_course=course_id)
    notes = list()
    for l in lessons:
        steps = Step.objects.all().filter(from_lesson=l.id).order_by('id')
        for s in steps:
            notes.append({'id': 'Step' + str(s.id) + 'from' + str(s.from_lesson), 'text': s.text_data})
    args = {'notes': notes}
    return render_to_response('notes_page.html', args, context_instance=RequestContext(request))


def error500_handler(request):
    logger.exception('Unknown internal server error')
    if 'HTTP_REFERER' in request.META:
        args = {'go_back': request.META['HTTP_REFERER'],
                'full_name': request.user.username}
    else:
        args = {'go_back': '/'}

    args['sentry_id'] = request.sentry['id']
    args.update(csrf(request))
    return render_to_response('internal_error.html', args, context_instance=RequestContext(request))


def error_description(request, description='Unknown error'):
    if 'HTTP_REFERER' in request.META:
        args = {'go_back': request.META['HTTP_REFERER'],
                'full_name': request.user.username}
    else:
        args = {'go_back': '/'}

    args['description'] = description
    args.update(csrf(request))
    return render_to_response('error_description.html', args, context_instance=RequestContext(request))
