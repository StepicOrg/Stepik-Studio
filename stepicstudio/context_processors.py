from django.conf import settings

from stepicstudio.state import CURRENT_TASKS_DICT


def global_vars(request):
    if len(CURRENT_TASKS_DICT.items()) == 0:
        return {'GLOB_TASKS': None}
    else:
        return {'GLOB_TASKS': 'Something recording'}


def autofocus_enabled(request):
    return {'AF_ENABLED': settings.ENABLE_REMOTE_AUTOFOCUS}
