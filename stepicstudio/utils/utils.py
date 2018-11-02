from stepicstudio.models import Course, CameraStatus
from stepicstudio.const import *


def url_to_args(url):
    answ = url.split('/')
    args = {}
    if COURSE_ULR_NAME in answ:
        id_ = answ[answ.index(COURSE_ULR_NAME) + 1]
        course = Course.objects.get(id=id_)
        args.update({'Course': course})

    if LESSON_URL_NAME in answ:
        args.update({'Lesson': answ[answ.index(LESSON_URL_NAME) + 1]})

    if STEP_URL_NAME in answ:
        args.update({'Step': answ[answ.index(STEP_URL_NAME) + 1]})
    return args


def camera_curr_status():
    return CameraStatus.objects.get(id='1').status


def bytes2human(n) -> str:
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return '%sB' % n


def human2bytes(s):
    num = ''
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    while s and s[0:1].isdigit() or s[0:1] == '.':
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    if letter not in symbols:
        raise ValueError('can\'t interpret %r' % s)
    prefix = {symbols[0]: 1}
    for i, s in enumerate(symbols[0:]):
        prefix[s] = 1 << (i + 1) * 10
    return int(num * prefix[letter])
