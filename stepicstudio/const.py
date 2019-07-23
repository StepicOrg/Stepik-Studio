import os
from sys import platform as _platform

from django.conf import settings

COURSE_ULR_NAME = 'course'
LESSON_URL_NAME = 'lesson'
STEP_URL_NAME = 'step'
SUBSTEP_URL_NAME = None

TS_EXTENSION = '.TS'
MP4_EXTENSION = '.mp4'
MKV_EXTENSION = '.mkv'

SYNC_LABEL = '_Synchronized'
RAW_CUT_LABEL = '_Raw_Cut'

SUBSTEP_PROFESSOR = '_Camera' + MP4_EXTENSION
SUBSTEP_SCREEN = '_Screen' + MP4_EXTENSION
RAW_CUT_POSTFIX = RAW_CUT_LABEL + MP4_EXTENSION

SCREEN_LABEL = os.path.splitext(SUBSTEP_SCREEN)[0]
PROFESSOR_LABEL = os.path.splitext(SUBSTEP_PROFESSOR)[0]

PROFESSOR_IP = settings.PROFESSOR_IP

FFMPEG_PATH = settings.FFMPEG_PATH

RAW_CUT_FOLDER_NAME = 'RawCut'

if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    FFPROBE_RUN_PATH = 'ffprobe'
else:
    FFPROBE_RUN_PATH = settings.FFPROBE_RUN_PATH

FFMPEGcommand = FFMPEG_PATH + settings.FFMPEG_CMD_PART
