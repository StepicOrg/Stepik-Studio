from django.conf import settings


def autofocus_enabled(request):
    return {'AF_ENABLED': settings.ENABLE_REMOTE_AUTOFOCUS}


def username(request):
    return {'full_name': request.user.username}
