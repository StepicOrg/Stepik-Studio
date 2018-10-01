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
PROFESSOR_IP = settings.PROFESSOR_IP
FFMPEG_PATH = settings.FFMPEG_PATH

FFPROBE_RUN_PATH = 'ffprobe' if _platform in ['linux', 'linux2', 'darwin'] else settings.FFPROBE_RUN_PATH

FFMPEGcommand = FFMPEG_PATH + settings.FFMPEG_CMD_PART
