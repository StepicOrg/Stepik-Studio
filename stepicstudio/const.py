from sys import platform as _platform

COURSE_ULR_NAME = 'course'
LESSON_URL_NAME = 'lesson'
STEP_URL_NAME = 'step'
SUBSTEP_URL_NAME = None
# SUBSTEP_PROFESSOR = 'Professor.f4v'
SUBSTEP_PROFESSOR = '_Professor.TS'
SUBSTEP_PROFESSOR_v1 = 'Professor.TS'
SUBSTEP_SCREEN = '_Screen.mkv'
SUBSTEP_SCREEN_v1 = 'Screen.mkv'
##PROFESSOR_IP = '172.21.202.96'
PROFESSOR_IP = '172.21.202.109'
FFMPEG_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'

if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    FFPROBE_RUN_PATH = 'ffprobe'
else:
    FFPROBE_RUN_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'