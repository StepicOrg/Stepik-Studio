import logging

from django.conf import settings
from django.utils.module_loading import import_string
from singleton_decorator import singleton

from stepicstudio.operations_statuses.operation_result import InternalOperationResult

logger = logging.getLogger(__name__)


@singleton
class AutofocusController(object):
    def __init__(self):
        if settings.AUTOFOCUS_MODULE.__len__() == 0:
            return

        pp_class = import_string(settings.AUTOFOCUS_MODULE)
        try:
            self.pp_instance = pp_class()
        except Exception as e:
            logger.warning('Can\'t load %s autofocus module: %S', pp_class, e)

    def focus_camera(self) -> InternalOperationResult:
        return self.pp_instance.focus_camera()
