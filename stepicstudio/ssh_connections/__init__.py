from django.conf import settings


def get_full_linux_path(substep):
    return settings.LINUX_DIR + substep.os_tablet_path
