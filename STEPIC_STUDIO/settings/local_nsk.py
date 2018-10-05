from .base import *

LINUX_DIR = '/home/user/VIDEO/STEPICSTUDIO/'

ALLOWED_HOSTS = ['172.25.202.31', '127.0.0.1']

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
        'PASSWORD': 'wowsostepik',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

PROFESSOR_IP = '172.25.202.32'

UBUNTU_USERNAME = 'user'
UBUNTU_PASSWORD = '12345678'

# FFMPEG configuration
FFMPEG_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'
FFPROBE_RUN_PATH = r'D:\VIDEO\ffmpeg\bin\ffprobe.exe'
FFMPEG_CMD_PART = r' -y -f dshow -video_size 1920x1080 -rtbufsize 1024M -framerate 25 -i video="Blackmagic WDM ' \
                  'Capture":audio="Blackmagic WDM Capture" -codec:v libx264 -preset ultrafast -crf 17 '

FFMPEG_TABLET_CMD = r'ffmpeg -f alsa -ac 2 -i pulse -f x11grab -r 24 -s 1920x1080 -i :0.0 ' \
                     '-pix_fmt yuv420p -vcodec libx264 -acodec pcm_s16le -preset ultrafast -threads 0 -af ' \
                     '"volume=1dB" -y '

# should reencode .TS to .mp4, where {0} - input file, {1} - output file
CAMERA_REENCODE_TEMPLATE = r'-y -i {0} -c copy {1}'

# should reencode .mkv to .mp4, where {0} - input file, {1} - output file
TABLET_REENCODE_TEMPLATE = r'-y -i {0} -c:v copy {1}'

SILENCE_DETECT_TEMPLATE = r'-i {} -af silencedetect=n={}:d={} -f null -'

VIDEO_OFFSET_TEMPLATE = r'-y -itsoffset {0} -i {1} -async 1 {2}'  # 0 - duration, 1 - input file, 2  - output file

# time in hours (24h format) when background tasks (e.g. video synchronizing) executes
BACKGROUND_TASKS_START_HOUR = '02'
