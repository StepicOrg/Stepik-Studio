from stepicstudio.models import Course, Lesson, Step, SubStep, UserProfile, CameraStatus
from stepicstudio.const import *


def url_to_args(url):
    answ = url.split("/")
    args = {}
    # print(answ, COURSE_ULR_NAME)
    if COURSE_ULR_NAME in answ:
        id_ = answ[answ.index(COURSE_ULR_NAME) + 1]
        course = Course.objects.get(id=id_)
        args.update({"Course": course})

    if LESSON_URL_NAME in answ:
        args.update({"Lesson": answ[answ.index(LESSON_URL_NAME) + 1]})

    if STEP_URL_NAME in answ:
        args.update({"Step": answ[answ.index(STEP_URL_NAME) + 1]})
    return args


def camera_curr_status():
    return CameraStatus.objects.get(id="1").status