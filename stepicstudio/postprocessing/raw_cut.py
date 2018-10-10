import logging

from django.conf import settings

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class RawCutter(object):
    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__logger = logging.getLogger(__name__)

    def raw_cut(self, video_path1: str, video_path2: str, output_path: str) -> InternalOperationResult:
        status_1 = self.__fs_client.validate_file(video_path1)
        status_2 = self.__fs_client.validate_file(video_path2)

        if not status_1 or not status_2:
            self.__logger.warning('Can\'t process invalid videos: %s, %s', video_path1, video_path2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        command = settings.FFMPEG_PATH + ' ' \
                  + settings.RAW_CUT_TEMPLATE.format(video_path1, video_path2, output_path)

        status, process = self.__fs_client.execute_command(command)

        if status.status is not ExecutionStatus.SUCCESS:
            return status
