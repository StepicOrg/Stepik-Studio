from .base import *

LINUX_DIR = '/home/stepic/VIDEO/STEPICSTUDIO/'

ALLOWED_HOSTS = ['172.25.203.148', '127.0.0.1']

# Capacity warnings low borders:
WARNING_CAPACITY = 100 * 1024 * 1024 * 1024  # 100GB
ERROR_CAPACITY = 20 * 1024 * 1024 * 1024  # 20GB

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stepicstudio_db',
        'USER': 'postgres',
        'PASSWORD': 'wowdatabase',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

PROFESSOR_IP = '172.25.203.148'

UBUNTU_USERNAME = 'stepic'
UBUNTU_PASSWORD = 'wowstepik'

# FFMPEG configuration
FFMPEG_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'
FFPROBE_RUN_PATH = r'D:\VIDEO\ffmpeg\bin\ffprobe.exe'
FFMPEG_CMD_PART = r' -f dshow -video_size 1920x1080 -rtbufsize 702000k -framerate 25 -i video="Decklink Video ' \
                            r'Capture":audio="MAIN (QUAD-CAPTURE)" -threads 0  -preset ultrafast  -c:v libx264 '

FFMPEG_TABLET_CMD = r'ffmpeg -f alsa -ac 2 -i pulse -f x11grab -draw_mouse 0 -r 24 -s 1920x1080 -i :0.0 ' \
                  '-pix_fmt yuv420p -vcodec libx264 -acodec pcm_s16le -preset ultrafast -threads 0 -af "volume=1dB" -y '

# should reencode .TS to .mp4, where {0} - input file, {1} - output file
CAMERA_REENCODE_TEMPLATE = r'-y -i {0} -c copy {1}'

# should reencode .mkv to .mp4, where {0} - input file, {1} - output file
TABLET_REENCODE_TEMPLATE = r'-y -i {0} -c:v copy {1}'

SILENCE_DETECT_TEMPLATE = r'-i {} -af silencedetect=n={}:d={} -f null -'

VIDEO_OFFSET_TEMPLATE = r'-y -itsoffset {0} -i {1} -async 1 {2}'  # 0 - duration, 1 - input file, 2  - output file

BACKGROUND_TASKS_START_HOUR = '02'  # time in hours when background tasks (e.g. video synchronizing) executes

