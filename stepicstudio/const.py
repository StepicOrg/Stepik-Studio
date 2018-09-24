from sys import platform as _platform
from django.conf import settings

COURSE_ULR_NAME = 'course'
LESSON_URL_NAME = 'lesson'
STEP_URL_NAME = 'step'
SUBSTEP_URL_NAME = None
# SUBSTEP_PROFESSOR = 'Professor.f4v'
SUBSTEP_PROFESSOR = '_Professor.TS'
SUBSTEP_PROFESSOR_v1 = 'Professor.TS'
SUBSTEP_SCREEN = '_Screen.mkv'
SUBSTEP_SCREEN_v1 = 'Screen.mkv'
FAST_MONTAGE = '_Raw_Montage.mp4'
##PROFESSOR_IP = '172.21.202.96'
PROFESSOR_IP = settings.PROFESSOR_IP
FFMPEG_PATH = settings.FFMPEG_PATH

if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    FFPROBE_RUN_PATH = 'ffprobe'
else:
    FFPROBE_RUN_PATH = settings.FFPROBE_RUN_PATH

FFMPEGcommand = FFMPEG_PATH + settings.FFMPEG_COMM_PART
