from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from stepicstudio.models import Course, Lesson, Step, SubStep, UserProfile, CameraStatus
from stepicstudio.forms import LessonForm, StepForm
from stepicstudio.VideoRecorder.action import *
from stepicstudio.FileSystemOperations.action import search_as_files
from stepicstudio.utils.utils import *
import itertools
from django.db.models import Max
from stepicstudio.statistic import add_stat_info
import time
import requests
from wsgiref.util import FileWrapper
from STEPIC_STUDIO.settings import STATISTIC_URL, SECURE_KEY_FOR_STAT

def can_edit_page(view_function):
    def process_request(*args, **kwargs):
        access = test_access(args[0].user.id, list(filter(None, args[0].path.split("/"))))
        print("runing " + str(args[0].user.id) + str(kwargs['courseId']))
        # if cant_edit_course(args[0].user.id, kwargs['courseId']):
        if not access:
            return HttpResponseRedirect("/login/")
        else:
            print(args[0].user.id)
            return view_function(*args, **kwargs)
    return process_request


def cant_edit_course(user_id, course_id):
    courses_from_user_id = Course.objects.all().filter(editors=user_id)
    course = Course.objects.all().filter(id=course_id)[0]
    print(course)
    print(courses_from_user_id)
    if course in courses_from_user_id:
        return False
    else:
        return True

##TODO: Add substep checks
def test_access(user_id, path_list):
    if COURSE_ULR_NAME in path_list:
        course_id = path_list[path_list.index(COURSE_ULR_NAME)+1]
    else:
        course_id = None
    if LESSON_URL_NAME in path_list:
        lesson_id = path_list[path_list.index(LESSON_URL_NAME)+1]
    else:
        lesson_id = None
    if STEP_URL_NAME in path_list:
        step_id = path_list[path_list.index(STEP_URL_NAME)+1]
    else:
        step_id = None
    print("NOW " + str(user_id) + " " + str(course_id))
    print(cant_edit_course(user_id, course_id))
    if path_list[0] == COURSE_ULR_NAME and not cant_edit_course(user_id, course_id):
        print(path_list)
        if lesson_id and not (str(Lesson.objects.all().get(id=lesson_id).from_course) == str(course_id)):
            print(lesson_id,  Lesson.objects.all().get(id=lesson_id).from_course, course_id )
            print("Error here 1 ")
            return False
        if step_id and not (int(Step.objects.all().get(id=step_id).from_lesson) == int(lesson_id)):
            print("Error here 2 ")
            return False
        return True
    else:

        print("bla3 ")
        return False


def index(request):
    return login(request)


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response("login.html", c)


def logout(request):
    auth.logout(request)
    return render_to_response('base.html')

@login_required(login_url='/login/')
def get_user_courses(request):
    args = {'full_name': request.user.username, "Courses": Course.objects.all().filter(editors=request.user.id)}
    args.update({"Recording": camera_curr_status})
    return render_to_response("courses.html", args)


@login_required(login_url='/login/')
@can_edit_page
def get_course_page(request, courseId):
    lesson_list = [l for l in Lesson.objects.all().filter(from_course=courseId)]
    lesson_list.sort(key=lambda lesson: lesson.position)
    args = {'full_name': request.user.username, "Course": Course.objects.all().filter(id=courseId)[0],
                                                "Lessons": lesson_list}
    args.update({"Recording": camera_curr_status})
    return render_to_response("course_view.html", args)


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username = username, password = password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect("/loggedin/")
    else:
        return HttpResponseRedirect("/login/")


def loggedin(request):
    if request.user.is_authenticated():
        return render_to_response("loggedin.html", {'full_name': request.user.username, "Courses": Course.objects.all()})
    else:
        return HttpResponseRedirect("/login/")


##TODO: Implement correctly !!! REDECORATE WITH CAN_EDIT_PAGE
@login_required(login_url='/login/')
def add_lesson(request):
    if request.POST:
        form = LessonForm(request.user.id, request.POST)
        if form.is_valid():
            from_course = form.data["from_courseName"]
            saved_lesson = form.lesson_save()
            last_saved = Lesson.objects.get(id=saved_lesson.pk)
            last_saved.from_course = from_course
            last_saved.save()
            return HttpResponseRedirect('/course/'+from_course+"/")
    else:
        form = LessonForm(request.user.id)

    args = {"full_name": request.user.username, }
    args.update(csrf(request))
    args.update({"Recording": camera_curr_status})
    args['form'] = form
    return render_to_response("create_lesson.html", args)


@login_required(login_url='/login/')
@can_edit_page
def show_lesson(request, courseId, lessonId):
    args = {"full_name": request.user.username, "Course": Course.objects.all().filter(id=courseId)[0],
                                                       "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                                                       "Steps": Step.objects.all().filter(from_lesson=lessonId)}
    args.update({"Recording": camera_curr_status})
    return render_to_response("lesson_view.html", args)


@login_required(login_url='/login/')
@can_edit_page
def delete_lesson(request, courseId, lessonId):
    lesson_obj = Lesson.objects.get(id=lessonId)
    redirect_to_course_page = request.path.split("/")
    if not delete_files_associated(redirect_to_course_page):
        raise Exception("Cant delete files")
    for step in Step.objects.all().filter(from_lesson=lessonId):
        for substep in SubStep.objects.all().filter(from_step=step.pk):
            substep.delete()
        step.delete()
    lesson_obj.delete()
    return HttpResponseRedirect('/'+'/'.join(redirect_to_course_page[1:3])+'/')


##IMPLEMENT CORRECTLY

@login_required(login_url='/login/')
@can_edit_page
def add_step(request, courseId, lessonId):
    if request.POST:
        form = StepForm(request.user.id, lessonId, request.POST)
        if form.is_valid():
            from_lesson = form.data["from_lessonId"]
            saved_step = form.step_save()
            last_saved = Step.objects.get(id=saved_step.pk)
            last_saved.from_lesson = from_lesson
            last_saved.save()
            return HttpResponseRedirect('/' + COURSE_ULR_NAME + '/' + courseId + '/' + LESSON_URL_NAME + '/' + from_lesson + '/')
    else:
        form = StepForm(request.user.id, lessonId)

    args = {"full_name": request.user.username, "postUrl": "/" + COURSE_ULR_NAME + "/"+courseId+"/" + LESSON_URL_NAME
                                                                                + "/"+lessonId+"/add_step/"}
    args.update({"Recording": camera_curr_status})
    args.update(csrf(request))
    args['form'] = form
    return render_to_response("create_step.html", args)



@login_required(login_url='/login/')
@can_edit_page
def show_step(request, courseId, lessonId, stepId):
    postURL = "/" + COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/" + STEP_URL_NAME + "/" + stepId + "/"
    args =  {"full_name": request.user.username, "Course": Course.objects.all().get(id=courseId),
                                                     "Lesson": Lesson.objects.all().get(id=lessonId),
                                                     "Step": Step.objects.get(id=stepId),
                                                     "postUrl": postURL,
                                                     "SubSteps": SubStep.objects.all().filter(from_step=stepId), }
    args.update({"Recording": camera_curr_status})
    return render_to_response("step_view.html", args)


#TODO: ADD RERECORD FUNCTION HERE
## TODO: ADD DECORATOR can_edit_page
## TODO: TOKEN at POSTrequest to statistic server is insecure
@login_required(login_url='/login/')
@can_edit_page
def start_new_step_recording(request, courseId, lessonId, stepId):
    substep = SubStep()
    substep.from_step = stepId
    stepIndex = len(SubStep.objects.all().filter(from_step=stepId)) + 1
    substep.name = "Step"+str(stepIndex)+"from"+str(substep.from_step)
    while SubStep.objects.filter(name=substep.name).count():
        stepIndex += 1
        substep.name = "Step"+str(stepIndex)+"from"+str(substep.from_step)
    substep.save()
    postURL = "/" + COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/" + STEP_URL_NAME + "/" + stepId + "/"
    args = {"full_name": request.user.username, "Course": Course.objects.all().filter(id=courseId)[0],
                                                "postUrl": postURL,
                                                "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                                                "Step": Step.objects.all().filter(id=stepId)[0],
                                                "SubSteps": SubStep.objects.all().filter(from_step=stepId),
                                                "currSubStep": SubStep.objects.get(id=substep.pk)}
    args.update(csrf(request))
    is_started = start_recording(user_id=request.user.id, user_profile=UserProfile.objects.get(user=request.user.id), data=args)
    if is_started:
        args.update({"Recording": True})
        args.update({"StartTime": CameraStatus.objects.get(id="1").start_time / 1000})
    try:
        print("sent data to stepic.mehanig.com")
        data = {'User': request.user.username, 'Name': substep.name, 'Duration': 'No data', 'priority':'1', 'status':'0',
                'token': SECURE_KEY_FOR_STAT}
        r = requests.post(STATISTIC_URL, data=data)
        print('STATISTIC STATUS:', r)
    except Exception as e:
        print('Error!!!: ', e)

    return render_to_response("step_view.html", args)


@login_required(login_url='/login')
def recording_page(request, courseId, lessonId, stepId):
    postURL = "/" +  COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/" + STEP_URL_NAME + "/" + stepId + "/"
    args = {"full_name": request.user.username, "Course": Course.objects.all().filter(id=courseId)[0],
                                                "postUrl": postURL,
                                                "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                                                "Step": Step.objects.all().filter(id=stepId)[0],
                                                "SubSteps": SubStep.objects.all().filter(from_step=stepId), }
    args.update({"Recording": camera_curr_status})
    return render_to_response("step_view.html", args)

##TODO: Add statistic here
@login_required(login_url='/login')
@can_edit_page
def stop_all_recording(request):
        args = {"full_name": request.user.username }
        args.update(csrf(request))
        stop_cam_recording()
        args.update({"Recording": camera_curr_status})
        return render_to_response("courses.html", args)

@login_required(login_url="/login")
@can_edit_page
def stop_recording(request, courseId, lessonId, stepId):
        postURL = "/" +  COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/" + STEP_URL_NAME + "/" + stepId + "/"
        args = {"full_name": request.user.username, "Course": Course.objects.all().filter(id=courseId)[0],
                "postUrl": postURL, "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                "Step": Step.objects.all().filter(id=stepId)[0],
                "SubSteps": SubStep.objects.all().filter(from_step=stepId), }
        args.update(csrf(request))
        stop_cam_recording()
        args.update({"Recording": camera_curr_status})
        last_substep_time = SubStep.objects.all().filter(from_step=stepId).aggregate(Max('start_time'))['start_time__max']
        recorded_substep = SubStep.objects.all().filter(start_time=last_substep_time)[0]
        add_stat_info(recorded_substep.id)
        return HttpResponseRedirect(postURL, args)




@login_required(login_url='/login/')
@can_edit_page
def remove_substep(request, courseId, lessonId, stepId, substepId):
    substep = SubStep.objects.get(id=substepId)
    postURL = "/" +  COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/" + STEP_URL_NAME + "/" + stepId + "/"
    args = {"full_name": request.user.username,
                                                     "Course": Course.objects.all().filter(id=courseId)[0],
                                                     "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                                                     "Step": Step.objects.all().filter(id=stepId)[0],
                                                     "postUrl": postURL,
                                                     "SubSteps": SubStep.objects.all().filter(from_step=stepId),
                                                     "currSubStep": substep}

    substep_deleted = delete_substep_files(user_id=request.user.id,
                                           user_profile=UserProfile.objects.get(user=request.user.id), data=args)
    substep.delete()
    #return render_to_response("step_view.html", args)
    return HttpResponseRedirect(postURL)

@login_required(login_url="/login/")
@can_edit_page
def delete_step(request, courseId, lessonId, stepId):
    step = Step.objects.all().get(id=stepId)
    postURL = "/" +  COURSE_ULR_NAME + "/" + courseId + "/" + LESSON_URL_NAME + "/"+lessonId+"/"
    args = {"full_name": request.user.username,
                                                     "Course": Course.objects.all().filter(id=courseId)[0],
                                                     "Lesson": Lesson.objects.all().filter(id=lessonId)[0],
                                                     "Step": Step.objects.all().filter(id=stepId)[0],
                                                     "postUrl": postURL,
                                                     "SubSteps": SubStep.objects.all().filter(from_step=stepId)}
    substeps = SubStep.objects.all().filter(from_step=stepId)
    for substep in substeps:
        # args['currSubStep'] = substep
        # substep_deleted = delete_substep_files(user_id=request.user.id,
        #                                    user_profile=UserProfile.objects.get(user=request.user.id), data=args)
        substep.delete()
    step_deleted = delete_step_files(user_id=request.user.id,
                                            user_profile=UserProfile.objects.get(user=request.user.id), data=args)
    step.delete()
    return HttpResponseRedirect(postURL)


### ADD DECORATOR can_edit_page ###
@login_required(login_url='/login/')
def rerecord_substep(request, courseId, lessonId, stepId, substepId):
    pass


@login_required(login_url='/login/')
def user_profile(request):
    return render_to_response("UserProfile.html", {"full_name": request.user.username,
                                                  "settings": UserProfile.objects.get(user_id=request.user.id),
                                                  })

##TODO: Refactor
def reorder_elements(request):
    if request.POST and request.is_ajax():
        args = url_to_args(request.META['HTTP_REFERER'])
        args.update({"user_profile": UserProfile.objects.get(user=request.user.id)})
        if "Course" in args and not "Lesson" in args:
            neworder = request.POST.getlist('ids[]')
            for i in range(len(neworder)):
                id = neworder[i]
                if id == '':
                    break
                l = Lesson.objects.get(id=id)
                l.position = i
                l.save()
            #database.lock()
        files_update(**args)
    else:
        return Http404

@login_required(login_url="/login/")
@can_edit_page
def show_course_struct(request, courseId):
    args = {"full_name": request.user.username, "Course": Course.objects.all().get(id=courseId)}
    args.update({"user_profile": UserProfile.objects.get(user=request.user.id)})
    args.update({"Recording": camera_curr_status})
    all_lessons = Lesson.objects.all().filter(from_course=courseId)
    args.update({"all_course_lessons": all_lessons})
    all_steps = ()
    for l in all_lessons:
        steps = Step.objects.all().filter(from_lesson=l.pk)
        all_steps = itertools.chain(all_steps, steps)
    all_steps = list(all_steps)
    args.update({"all_steps": all_steps})
    args = search_as_files(args)
    args.update(csrf(request))
    return render_to_response("course_struct.html", args)

@login_required(login_url="/login/")
@can_edit_page
def view_stat(request, courseId):
    args = {"full_name": request.user.username, "Course": Course.objects.all().get(id=courseId)}
    return render_to_response("stat.html", args)



###TODO: try catch works incorrectly. Should check for file size before return
def video_view(request, substepId):
    substep = SubStep.objects.all().get(id=substepId)
    try:
        file = FileWrapper(open(substep.os_path, 'rb'))
        response = HttpResponse(file, content_type='video/TS')
        response['Content-Disposition'] = 'inline; filename='+substep.name+"_"+SUBSTEP_PROFESSOR
        return response
    except Exception as e:
        print(e)
        return HttpResponse("File to large. Please watch it on server.")

def video_screen_view(request, substepId):
    substep = SubStep.objects.all().get(id=substepId)
    try:
        path = '/'.join((list(filter(None, substep.os_path.split("/"))))[:-1]) + "/" + SUBSTEP_SCREEN
        file = FileWrapper(open(path, 'rb'))
        response = HttpResponse(file, content_type='video/mkv')
        response['Content-Disposition'] = 'inline; filename='+substep.name+"_"+SUBSTEP_SCREEN
        return response
    except Exception as e:
        print(e)
        return HttpResponse("File to large. Please watch it on server.")
