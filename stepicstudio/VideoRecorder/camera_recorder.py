import logging
import subprocess

from singleton_decorator import singleton

from stepicstudio.FileSystemOperations.file_system_client import FileSystemClient
from stepicstudio.const import FFMPEGcommand
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus


@singleton
class ServerCameraRecorder(object):
    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__command = FFMPEGcommand
        self.__process = None
        self.__logger = logging.getLogger('stepic_studio.FileSystemOperations.camera_recorder')

    def start_recording(self, path: str, filename: str) -> InternalOperationResult:
        if self.is_active():
            self.__logger.error('Can\'t start FFMPEG for file %s: camera is acctually recording (process with PID %s)',
                                path + '\\' + filename,
                                self.__process.pid)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Camera is actually recording')

        local_command = self.command + path + '\\' + filename
        result, self.__process = self.__fs_client.execute_command(local_command)

        if result.status is ExecutionStatus.SUCCESS:
            self.__logger.info('Successful starting FFMPEG (PID: %s; FFMPEG command: %s)',
                               self.__process.pid, local_command)
        else:
            self.__logger.error('FFMPEG start failed: %s; command: %s', result.message, local_command)

        return result

    def stop_recording(self) -> InternalOperationResult:
        if self.__process is None:
            self.__logger.error('Can\'t stop non existing FFMPEG process')
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Can\'t stop non existing FFMPEG process')

        result = self.__fs_client.kill_process(self.__process.pid)

        if result.status is ExecutionStatus.SUCCESS:
            self.__logger.info('Successfully stop FFMPEG process (PID: %s)', self.__process.pid)
            self.__process = None
            return result
        else:
            self.__logger.error('Can\'t stop FFMPEG process (PID: %s) : %s', self.__process.pid, result.message)
            return result

    def is_active(self) -> bool:
        return self.__process is not None
