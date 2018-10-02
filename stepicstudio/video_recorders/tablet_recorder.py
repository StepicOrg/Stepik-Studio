from singleton_decorator import singleton
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections.tablet_client import TabletClient
from stepicstudio.video_recorders.postprocessable_recorder import PostprocessableRecorder
from django.conf import settings


@singleton
class TabletScreenRecorder(PostprocessableRecorder):
    def __init__(self):
        super().__init__()
        self.__tablet_client = TabletClient()
        self.__command = settings.FFMPEG_TABLET_CMD
        self.__last_processed_path = None
        self.__last_processed_file = None
        self._load_postprocessing_pipe(settings.TABLET_POSTPROCESSING_PIPE)

    def start_recording(self, path: str, filename: str) -> InternalOperationResult:
        if self.is_active():
            self.__logger.error('Can\'t start FFMPEG for file %s: screen is acctually recording ', path + '/' + filename)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Tablet is actually recording')

        # local_command = self.__command + os.path.join(path, filename)

    def stop_recording(self) -> InternalOperationResult:
        pass

    def is_active(self) -> bool:
        pass
