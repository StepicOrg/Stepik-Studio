import logging

from django.conf import settings

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class RawCutter(object):
    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__logger = logging.getLogger(__name__)
        self.__process = None

    def raw_cut(self, substep: SubStep):
        pass

    def __internal_raw_cut(self, video_path1: str, video_path2: str, output_path: str) -> InternalOperationResult:
        status_1 = self.__fs_client.validate_file(video_path1)
        status_2 = self.__fs_client.validate_file(video_path2)

        if not status_1 or not status_2:
            self.__logger.warning('Can\'t process invalid videos: %s, %s', video_path1, video_path2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        command = settings.FFMPEG_PATH + ' ' + \
                  settings.RAW_CUT_TEMPLATE.format(video_path1, video_path2, output_path)

        status = self.__fs_client.execute_command_sync(command)

        if status.status is not ExecutionStatus.SUCCESS:
            return status

    def __cancel(self):
        if self.__process is not None:
            pid = self.__process.pid
            if self.__fs_client.is_process_exists(pid):
                self.__fs_client.kill_process(pid)
                self.__process = None

    def __get_target_files(self, path) -> (str, str):
        # synced_file if contains
        # else mp4
        # els TS + mkv
        pass
