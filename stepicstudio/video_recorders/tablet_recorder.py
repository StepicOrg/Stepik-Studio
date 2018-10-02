import logging

from singleton_decorator import singleton

from stepicstudio import const
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections.tablet_client import TabletClient
from stepicstudio.video_recorders.postprocessable_recorder import PostprocessableRecorder
from django.conf import settings


@singleton
class TabletScreenRecorder(PostprocessableRecorder):
    def __init__(self):
        super().__init__()
        self.__command = settings.FFMPEG_TABLET_CMD
        self.__logger = logging.getLogger('stepic_studio.video_recorders.tablet_recorder')
        self.__last_processed_path = None
        self.__last_processed_file = None
        self._load_postprocessing_pipe(settings.TABLET_POSTPROCESSING_PIPE)

        try:
            self.__tablet_client = TabletClient()
        except Exception as e:
            self.__logger.error('Can\'t initialize tablet client: %s', e)
            raise e

    def start_recording(self, path: str, filename: str) -> InternalOperationResult:
        if self.is_active():
            self.__logger.error('Can\'t start FFMPEG for file %s: screen is acctually recording ',
                                path + '/' + filename)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Tablet is actually recording')

        self.__tablet_client.check_and_create_folder(path)

        command = settings.FFMPEG_TABLET_CMD + path + filename + const.SUBSTEP_SCREEN + ' 2< /dev/null &'
        # local_command = self.__command + os.path.join(path, filename)

    def stop_recording(self) -> InternalOperationResult:
        command = 'pkill -f ffmpeg'

        try:
            self.__tablet_client.execute_remote(command)
        except Exception as e:
            self.__logger.error('Problems while stop screen recording: %s', e)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        return InternalOperationResult(ExecutionStatus.SUCCESS)

    def is_active(self) -> bool:
        pass
