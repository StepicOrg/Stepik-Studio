import copy
import itertools
import re

from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from stepicstudio.camera_controls import AutofocusController
from stepicstudio.forms import LessonForm, StepForm
from stepicstudio.models import UserProfile, Lesson, SubStep
from stepicstudio.postprocessing import start_subtep_montage, start_step_montage, start_lesson_montage
from stepicstudio.postprocessing.exporting import export_obj_to_prproj, get_target_step_files, \
    get_target_lesson_files, get_target_course_files
from stepicstudio.ssh_connections import delete_tablet_substep_files, delete_tablet_step_files, \
    delete_tablet_lesson_files
from stepicstudio.utils.utils import *
from stepicstudio.video_recorders.action import *
from stepicstudio.video_streaming import stream_video

logger = logging.getLogger('stepicstudio.views')


def can_edit_page(view_function):
    def process_request(*args, **kwargs):
        access = test_access(args[0].user.id, list(filter(None, args[0].path.split('/'))))
        if not access:
            return HttpResponseRedirect(reverse('stepicstudio.views.login'))
        else:
            return view_function(*args, **kwargs)

    return process_request


def ajax_required(view_function):
    def process_request(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return view_function(request, *args, **kwargs)

    return process_request


def cant_edit_course(user_id, course_id):
    courses_from_user_id = Course.objects.filter(editors=user_id)
    course = Course.objects.filter(id=course_id)[0]
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
        if lesson_id and not (str(Lesson.objects.get(id=lesson_id).from_course) == str(course_id)):
            return False
        if step_id and not (int(Step.objects.get(id=step_id).from_lesson) == int(lesson_id)):
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


@staff_member_required
def get_users_list(request):
    args = {'Users': UserProfile.objects.all().order_by('-last_visit'),
            'item_type': 'user'}
    return render_to_response('control_panel/base_control_panel.html', args, context_instance=RequestContext(request))


@staff_member_required
@ajax_required
@require_http_methods(['POST'])
def get_items(request):
    item_id = request.POST['item_id']
    requesting_item_type = request.POST['requesting_item_type']

    if requesting_item_type == 'user':
        args = {'Items': Course.objects.filter(editors=item_id).order_by('-start_date'),
                'item_type': 'course'}
        html = render_to_string('control_panel/courses_block.html', args)
    elif requesting_item_type == 'course':
        args = {'Items': Lesson.objects.filter(from_course=item_id).order_by('position', '-start_time'),
                'item_type': 'lesson'}
        html = render_to_string('control_panel/lessons_block.html', args)
    elif requesting_item_type == 'lesson':
        args = {'Items': Step.objects.filter(from_lesson=item_id).order_by('position', '-start_time'),
                'item_type': 'step'}
        html = render_to_string('control_panel/steps_block.html', args)
    elif requesting_item_type == 'step':
        args = {'Items': SubStep.objects.filter(from_step=item_id).order_by('-start_time'),
                'item_type': 'substep'}
        html = render_to_string('control_panel/substeps_block.html', args)
    elif requesting_item_type == 'substep':
        return HttpResponse()
    else:
        return HttpResponseBadRequest

    return HttpResponse(html)


@login_required(login_url='/login/')
def get_courses(request):
    args = {'Courses': Course.objects.filter(editors=request.user.id).order_by('-start_date')}
    args.update({'Recording': camera_curr_status})
    return render_to_response('courses.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def get_course_page(request, course_id):
    lesson_list = Lesson.objects.filter(from_course=course_id).order_by('position', '-start_time')
    args = {'Course': Course.objects.filter(id=course_id)[0],
            'Lessons': lesson_list}
    args.update({'Recording': camera_curr_status})
    return render_to_response('course_view.html', args, context_instance=RequestContext(request))


@require_http_methods(['POST'])
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user:
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
        args = {'say_hello': say_hello,
                'Courses': Course.objects.filter(editors=request.user.id).order_by('-start_date')}
        args.update(csrf(request))
        return render_to_response('loggedin.html', args, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('stepicstudio.views.login'))


@login_required(login_url='/login/')
@can_edit_page
def add_lesson(request, course_id):
    if request.method == 'GET':
        if request.META.get('HTTP_REFERER'):
            form = LessonForm(userId=request.user.id, from_course=course_id)
        else:
            raise Http404
    elif request.method == 'POST':
        form = LessonForm(request.POST, userId=request.user.id, from_course=course_id)
        if form.is_valid():
            saved_lesson = form.lesson_save()
            last_saved = Lesson.objects.get(id=saved_lesson.pk)
            last_saved.from_course = course_id
            last_saved.save()
            return HttpResponse('Ok')
    else:
        raise Http404

    args = {'form': form}
    args.update(csrf(request))
    return render_to_response('create_lesson.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def show_lesson(request, course_id, lesson_id):
    args = {'Course': Course.objects.filter(id=course_id).first(),
            'Lesson': Lesson.objects.filter(id=lesson_id).first(),
            'Steps': Step.objects.filter(from_lesson=lesson_id).order_by('position', '-start_time')}
    args.update({'Recording': camera_curr_status})
    return render_to_response('lesson_view.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def delete_lesson(request, course_id, lesson_id):
    try:
        lesson_obj = Lesson.objects.get(id=lesson_id)
        for step in Step.objects.filter(from_lesson=lesson_id):
            for substep in SubStep.objects.filter(from_step=step.pk):
                if substep.is_locked:
                    return error_description(request, 'Sorry, can\'t delete lesson\'s files. '
                                                      'Lesson contains locked substep.')
                else:
                    substep.delete()
            step.delete()
    except:
        logger.warning('Failed to delete lesson\'s files.')
        return error_description(request, 'Sorry, can\'t delete lesson\'s files. Error log will sent to developers.')

    if delete_lesson_on_disk(lesson_obj).status is ExecutionStatus.SUCCESS and \
            delete_tablet_lesson_files(lesson_obj).status is ExecutionStatus.SUCCESS:
        lesson_obj.delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        logger.warning('Failed to delete lesson\'s files.')
        return error_description(request, 'Sorry, can\'t delete lesson\'s files. Error log will sent to developers.')


@login_required(login_url='/login/')
@can_edit_page
def add_step(request, course_id, lesson_id):
    if request.POST:
        form = StepForm(lesson_id, request.POST)
        if form.is_valid():
            saved_step = form.step_save()
            last_saved = Step.objects.get(id=saved_step.pk)
            last_saved.from_lesson = lesson_id
            last_saved.save()
            return HttpResponse('Ok')
    else:
        form = StepForm(lesson_id)

    args = {'form': form}
    args.update(csrf(request))
    return render_to_response('create_step.html', args, context_instance=RequestContext(request))


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
            else:
                return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')
        else:
            raise Http404
    all_substeps = SubStep.objects.filter(from_step=step_id).order_by('-start_time')
    summ_time = update_time_records(all_substeps)
    step_obj.is_fresh = True
    step_obj.duration += summ_time
    step_obj.save()
    args = {'Course': Course.objects.get(id=course_id),
            'Lesson': Lesson.objects.get(id=lesson_id),
            'Step': Step.objects.get(id=step_id),
            'SubSteps': all_substeps,
            'tmpl_name': UserProfile.objects.get(user=request.user.id).substep_template,
            'Recording': camera_curr_status}

    args.update(csrf(request))
    return render_to_response('step_view.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login')
@can_edit_page
@ajax_required
def stop_recording(request, course_id, lesson_id, step_id):
    if stop_cam_recording():
        last_substep = SubStep.objects.filter(from_step=step_id).latest('start_time')
        update_time_records(None, new_step_only=True, new_step_obj=last_substep)
        args = {'Substep': last_substep,
                'tmpl_name': UserProfile.objects.get(user=request.user.id).substep_template}
        html = render_to_string('substep_block.html', args)
        return HttpResponse(html)
    else:
        return HttpResponseServerError('Sorry, there is some problems.\nError log will sent to developers.')


@login_required(login_url='/login')
@ajax_required
@require_http_methods(['POST'])
def notes(request, step_id):
    try:
        step_obj = Step.objects.get(id=step_id)
        step_obj.text_data = dict(request.POST.lists())['notes'][0]
        step_obj.save()
    except:
        return HttpResponseServerError()

    return HttpResponse('Ok')


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


@login_required(login_url='/login/')
def start_new_step_recording(request, course_id, lesson_id, step_id) -> InternalOperationResult:
    substep = SubStep()
    substep.from_step = step_id
    target_substeps = SubStep.objects.filter(from_step=step_id)

    try:
        last_ss_name = target_substeps.latest('start_time').name
        substep_index = re.findall(r'\d+', last_ss_name)[1] + 1  # index of latest substep
    except:
        substep_index = 1

    substep.name = str(substep.from_step) + '_' + str(substep_index)

    while target_substeps.filter(name=substep.name).count():
        substep_index += 1
        substep.name = str(substep.from_step) + '_' + str(substep_index)

    substep.save()

    recording_status = start_recording(substep)
    if recording_status.status is not ExecutionStatus.SUCCESS:
        substep.delete()
    return recording_status


@login_required(login_url='/login')
@ajax_required
def montage(request, substep_id):
    start_subtep_montage(substep_id)
    return HttpResponse('Ok')


@ajax_required
def step_montage(request, step_id):
    start_step_montage(step_id)
    return HttpResponse('Ok')


@ajax_required
def lesson_montage(request, lesson_id):
    start_lesson_montage(lesson_id)
    return HttpResponse('Ok')


@login_required(login_url='/login')
@ajax_required
@require_http_methods(['POST'])
def substep_statuses(request):
    ids = (dict(request.POST.lists()))['ids']
    result = {}

    for ss_id in ids:
        try:
            substep = SubStep.objects.get(id=int(ss_id))
            is_locked = substep.is_locked
            is_automontage_exists = substep.automontage_exist
            result[ss_id] = {'islocked': is_locked,
                             'exists': is_automontage_exists}
        except:
            pass

    return JsonResponse(result)


@csrf_exempt
def stop_all_recording(request):
    stop_cam_recording()
    return HttpResponse('Ok')


@login_required(login_url='/login/')
@can_edit_page
def delete_substep(request, course_id, lesson_id, step_id, substep_id):
    try:
        substep = SubStep.objects.get(id=substep_id)
    except:
        logger.exception('Can\'t delete substep')
        return HttpResponseServerError('Sorry, can\'t delete substep. An error log will be sent to the developers.')

    if substep.is_locked:
        return HttpResponseServerError('Sorry, can\'t delete locked substep. Please, wait for unlock.')

    server_remove_status = delete_substep_on_disk(substep)
    tablet_remove_status = delete_tablet_substep_files(substep)

    if server_remove_status.status is not ExecutionStatus.SUCCESS:
        logger.error('Can\'t delete substep, server error: %s', server_remove_status.message)
        return HttpResponseServerError('Sorry, can\'t delete substep. An error log will be sent to the developers.')

    if tablet_remove_status.status is not ExecutionStatus.SUCCESS:
        logger.error('Can\'t delete substep, tablet error: %s', tablet_remove_status.message)
        return HttpResponseServerError('Sorry, can\'t delete substep. An error log will be sent to the developers.')

    substep.delete()
    return HttpResponse('Ok')


@login_required(login_url='/login/')
@can_edit_page
def delete_step(request, course_id, lesson_id, step_id):
    try:
        step = Step.objects.get(id=step_id)
        substeps = SubStep.objects.filter(from_step=step_id)
    except:
        logger.warning('Failed to delete step files.')
        return error_description(request, 'Sorry, can\'t delete step files. Error log will sent to developers.')

    for ss in substeps:
        if ss.is_locked:
            return error_description(request, 'Sorry, can\'t delete step files. Step contains locked substep.')
        else:
            ss.delete()

    if delete_step_on_disk(step).status is ExecutionStatus.SUCCESS and \
            delete_tablet_step_files(step).status is ExecutionStatus.SUCCESS:
        step.delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        logger.warning('Failed to delete step files.')
        return error_description(request, 'Sorry, can\'t delete step files. Error log will sent to developers.')


@login_required(login_url='/login/')
def user_profile(request):
    return render_to_response('UserProfile.html',
                              {'settings': UserProfile.objects.get(user_id=request.user.id)},
                              context_instance=RequestContext(request))


# TODO: Refactor
@ajax_required
@require_http_methods(['POST'])
def reorder_elements(request):
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


@login_required(login_url='/login/')
@can_edit_page
def show_course_struct(request, course_id):
    args = {'Course': Course.objects.get(id=course_id)}
    args.update({'user_profile': UserProfile.objects.get(user=request.user.id)})
    args.update({'Recording': camera_curr_status})
    all_lessons = Lesson.objects.filter(from_course=course_id)
    args.update({'all_course_lessons': all_lessons})
    all_steps = ()
    for l in all_lessons:
        steps = Step.objects.filter(from_lesson=l.pk)
        all_steps = itertools.chain(all_steps, steps)
    all_steps = list(all_steps)
    args.update({'all_steps': all_steps})
    args = search_as_files_and_update_info(args)
    args.update(csrf(request))
    return render_to_response('course_struct.html', args, context_instance=RequestContext(request))


@login_required(login_url='/login/')
@can_edit_page
def view_stat(request, course_id):
    args = {'Course': Course.objects.get(id=course_id)}
    return render_to_response('stat.html', args, context_instance=RequestContext(request))


# TODO: This function is unsafe, its possible to watch other users files
@login_required(login_url='/login/')
def video_view(request, substep_id):
    try:
        substep = SubStep.objects.get(id=substep_id)
        if os.path.isfile(substep.os_path):
            return stream_video(request, substep.os_path)
        elif os.path.isfile(substep.os_path_old):
            return stream_video(request, substep.os_path_old)
        else:
            logger.warning('Missing camera recording file.')
            return error_description(request, 'File is missing.')
    except:
        return error500_handler(request)


@login_required(login_url='/login/')
def video_screen_view(request, substep_id):
    try:
        substep = SubStep.objects.get(id=substep_id)
        if os.path.isfile(substep.os_screencast_path):
            return stream_video(request, substep.os_screencast_path)
        elif os.path.isfile(substep.os_screencast_path_old):
            return stream_video(request, substep.os_screencast_path_old)
        else:
            logger.warning('Missing screencast file.')
            return error_description(request, 'File is missing.')
    except:
        return error500_handler(request)


@login_required(login_url='/login/')
def show_montage(request, substep_id):
    try:
        substep = SubStep.objects.get(id=substep_id)
        return stream_video(request, substep.os_automontage_file)
    except FileNotFoundError as e:
        logger.warning('Missing raw cut file: %s', e)
        return error_description(request, 'File is missing.')
    except:
        return error500_handler(request)


@ajax_required
@require_http_methods(['POST'])
def rename_elem(request):
    rest_data = dict(request.POST.lists())
    if 'step' in rest_data['type']:
        obj_to_rename = Step.objects.get(id=rest_data['id'][0])
    elif 'lesson' in rest_data['type']:
        obj_to_rename = Lesson.objects.get(id=rest_data['id'][0])
    else:
        raise Http404

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
        raise Http404



def clear_all_locked_substeps(request):
    all_locked = SubStep.objects.filter(is_locked=True)
    for ss in all_locked:
        ss.is_locked = False
        ss.save()
    return render_to_response('UserProfile.html',
                              {'settings': UserProfile.objects.get(user_id=request.user.id)},
                              context_instance=RequestContext(request))


def generate_notes_page(request, course_id):
    lessons = Lesson.objects.filter(from_course=course_id)
    notes = list()
    for l in lessons:
        steps = Step.objects.filter(from_lesson=l.id).order_by('id')
        for s in steps:
            notes.append({'id': 'Step' + str(s.id) + 'from' + str(s.from_lesson), 'text': s.text_data})
    args = {'notes': notes}
    return render_to_response('notes_page.html', args, context_instance=RequestContext(request))


@ajax_required
def autofocus_camera(request):
    if not settings.ENABLE_REMOTE_AUTOFOCUS:
        raise Http404

    result = AutofocusController().focus_camera()

    if result.status is ExecutionStatus.SUCCESS:
        return HttpResponse('Ok')
    else:
        logger.warning('Camera autofocus error: %s', result.message)
        return HttpResponseServerError(result.message)


@staff_member_required
@ajax_required
@require_http_methods(['POST'])
def export_prproj(request):
    item_id = request.POST['item_id']
    item_type = request.POST['item_type']

    try:
        if item_type == 'step':
            extractor = get_target_step_files
            db_obj = Step.objects.get(id=item_id)
        elif item_type == 'lesson':
            extractor = get_target_lesson_files
            db_obj = Lesson.objects.get(id=item_id)
        elif item_type == 'course':
            extractor = get_target_course_files
            db_obj = Course.objects.get(id=item_id)
        else:
            return HttpResponseBadRequest
    except:
        return HttpResponseServerError('{} with id {} not found'.format(item_type, item_id))

    result = export_obj_to_prproj(db_obj, extractor)

    if result.status is ExecutionStatus.SUCCESS:
        return HttpResponse('Ok')
    else:
        return HttpResponseServerError(result.message)


def error500_handler(request):
    logger.exception('Unknown internal server error')
    if 'HTTP_REFERER' in request.META:
        args = {'go_back': request.META['HTTP_REFERER']}
    else:
        args = {'go_back': '/'}

    args['sentry_id'] = request.sentry['id']
    args.update(csrf(request))
    return render_to_response('internal_error.html', args, context_instance=RequestContext(request))


def error_description(request, description='Unknown error'):
    if 'HTTP_REFERER' in request.META:
        args = {'go_back': request.META['HTTP_REFERER']}
    else:
        args = {'go_back': '/'}

    args['description'] = description
    args.update(csrf(request))
    return render_to_response('error_description.html', args, context_instance=RequestContext(request))
