from django.utils.timezone import now

from stepicstudio.FileSystemOperations.action import get_disk_info
from stepicstudio.models import UserProfile
import logging
from STEPIC_STUDIO.settings import ERROR_CAPACITY, WARNING_CAPACITY

from stepicstudio.utils.utils import bytes2human, human2bytes

logger = logging.getLogger('stepicstudio.middleware')


class SetLastVisitMiddleware(object):
    def process_response(self, request, response):
        try:
            if request.user.is_authenticated():
                UserProfile.objects.filter(pk=request.user.pk).update(last_visit=now())
        except Exception as e:
            logger.debug('Exception handled: %s', e)
            pass
        return response


class SetStorageCapacityMiddleware(object):
    def process_response(self, request, response):
        self.handle_server_space_info(request)
        return response

    def handle_server_space_info(self, request):
        try:
            user_server_path = UserProfile.objects.get(user=request.user.id).serverFilesFolder
            free_server_space, total_server_space = get_disk_info(user_server_path)
            request.session['free_space'] = bytes2human(free_server_space) + ' / ' + bytes2human(total_server_space)
            if free_server_space < human2bytes(ERROR_CAPACITY):
                request.session['server_space_status'] = 'error'
            elif free_server_space < human2bytes(WARNING_CAPACITY):
                request.session['server_space_status'] = 'warning'
            else:
                request.session['server_space_status'] = 'normal'
        except Exception as e:
            logger.warning("Can't get information about server disk capacity: %s", str(e))
            request.session['free_space'] = 'Err'
            request.session['server_space_status'] = 'normal'

