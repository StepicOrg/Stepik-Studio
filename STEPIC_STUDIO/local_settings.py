LINUX_DIR = '/home/user/VIDEO/STEPICSTUDIO/'

ALLOWED_HOSTS = ['172.25.202.31', '127.0.0.1']

# Capacity warnings low borders:
WARNING_CAPACITY = '100.0G'
ERROR_CAPACITY = '20.0G'

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

__PROFESSOR_IP = '172.25.202.32'

UBUNTU_USERNAME = 'user'
UBUNTU_PASSWORD = '12345678'

# FFMPEG configuration
__FFMPEG_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'
__FFPROBE_RUN_PATH = r'D:\VIDEO\ffmpeg\bin\ffprobe.exe'
__FFMPEG_COMM_PART =r' -y -f dshow -video_size 1920x1080 -rtbufsize 1024M -framerate 25 -i video="Blackmagic WDM Capture":audio="Blackmagic WDM Capture" -codec:v libx264 -preset ultrafast -crf 17 '