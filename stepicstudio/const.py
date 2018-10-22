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
RAW_MONTAGE_LABEL = '_Raw_Montage'

SUBSTEP_PROFESSOR = '_Professor' + TS_EXTENSION
SUBSTEP_PROFESSOR_v1 = 'Professor' + TS_EXTENSION
SUBSTEP_SCREEN = '_Screen' + MP4_EXTENSION
SUBSTEP_SCREEN_v1 = 'Screen' + MKV_EXTENSION
FAST_MONTAGE = RAW_MONTAGE_LABEL + MP4_EXTENSION

SCREEN_LABEL = os.path.splitext(SUBSTEP_SCREEN)[0]
PROFESSOR_LABEL = os.path.splitext(SUBSTEP_PROFESSOR)[0]

PROFESSOR_IP = settings.PROFESSOR_IP

FFMPEG_PATH = settings.FFMPEG_PATH

RAW_MONTAGE_FOLDER_NAME = 'RawMontage'

if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    FFPROBE_RUN_PATH = 'ffprobe'
else:
    FFPROBE_RUN_PATH = settings.FFPROBE_RUN_PATH

FFMPEGcommand = FFMPEG_PATH + settings.FFMPEG_CMD_PART
