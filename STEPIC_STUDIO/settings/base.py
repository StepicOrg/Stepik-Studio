"""
Django settings for STEPIC_STUDIO project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LINUX_DIR = ''

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '--+9q@q5n6@x-#!9&4p5k4yw@vfg+m9uk^#$qlqw8bv59y#@p='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

TEST = True

# Capacity warnings low borders:
WARNING_CAPACITY = 100 * 1024 * 1024 * 1024  # 100GB
ERROR_CAPACITY = 20 * 1024 * 1024 * 1024  # 20GB

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'stepicstudio',
)

MIDDLEWARE_CLASSES = (
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stepicstudio.middleware.SetStorageCapacityMiddleware',
    'stepicstudio.middleware.SetLastVisitMiddleware',
)

ROOT_URLCONF = 'STEPIC_STUDIO.urls'

WSGI_APPLICATION = 'STEPIC_STUDIO.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../static'),
)

TEMPLATE_DIRS = {'stepicstudio/templates/', }

UBUNTU_USERNAME = ''
UBUNTU_PASSWORD = ''

REST_FRAMEWORK = {

    'PAGE_SIZE': 10
}

PROFESSOR_IP = '172.25.202.32'

# FFMPEG configuration
FFMPEG_PATH = r'D:\VIDEO\ffmpeg\bin\ffmpeg.exe'
FFPROBE_RUN_PATH = r'D:\VIDEO\ffmpeg\bin\ffprobe.exe'
FFMPEG_CMD_PART = r' -y -f dshow -video_size 1920x1080 -rtbufsize 1024M -framerate 25 -i video="Blackmagic WDM Capture":audio="Blackmagic WDM Capture" -codec:v libx264 -preset ultrafast -crf 17 '

FFMPEG_TABLET_CMD = r'ffmpeg -f alsa -ac 2 -i pulse -f x11grab -r 24 -s 1920x1080 -i :0.0 ' \
                     '-pix_fmt yuv420p -vcodec libx264 -acodec pcm_s16le -preset ultrafast -threads 0 -af "volume=1dB" -y '

CAMERA_REENCODE_TEMPLATE = r'-y -i {0} -c copy {1}'  # should reencode .TS to .mp4

TABLET_REENCODE_TEMPLATE = r'-y -i {0} -c:v copy {1}'  # should reencode .mkv to .mp4

SILENCE_DETECT_TEMPLATE = r'-i {} -af silencedetect=n={}:d={} -f null -'

VIDEO_OFFSET_TEMPLATE = r'-y -itsoffset {0} -i {1} -async 1 {2}'  # 0 - duration, 1 - input file, 2  - output file

BACKGROUND_TASKS_START_HOUR = '02'  # time in hours when background tasks (e.g. video synchronizing) executes

RAVEN_CONFIG = {
    'dsn': 'https://efc5d55d068e4b3d9fa9c33a2359ef3a:2cf467c644d7404f9410f694a987cf6c@sentry.stepik.org/14',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'sentry': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/main.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_request.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'sentry': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
            'formatter': 'sentry'

        },
    },
    'loggers': {
        'raven': {
            'level': 'DEBUG',
            'handlers': ['default'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['default'],
            'propagate': False,
        },
        '': {
            'handlers': ['sentry', 'default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['sentry', 'request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# should contain handlers, which will applied to server recording
SERVER_POSTPROCESSING_PIPE = (
    'stepicstudio.postprocessing.postprocessors.TSConverter',
)

from django.conf import global_settings

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'stepicstudio.context_processors.global_vars',
    'django.core.context_processors.request'
)

try:
    from .local_nsk import *
except ImportError:
    pass
