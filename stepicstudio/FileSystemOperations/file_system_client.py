import logging
import subprocess
import psutil

from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus


class FileSystemClient(object):
    def __init__(self):
        self.logger = logging.getLogger('stepic_studio.FileSystemOperations.file_system_client')

    def execute_command(self, command: str) -> (InternalOperationResult, subprocess.Popen):
        try:
            proc = subprocess.Popen(command, shell=True)
            # process still running when returncode is None
            if proc.returncode is not None and proc.returncode != 0:
                _, error = proc.communicate()
                message = 'Cannot exec ffmpeg reencode command ({0}): {1}'.format(proc.returncode, error)
                self.logger.error(message)
                return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message), proc
        except Exception as e:
            message = 'Cannot exec ffmpeg reencode command: {0}'.format(str(e))
            self.logger.exception('Cannot exec ffmpeg reencode command: ')
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message), None

    def kill_process(self, pid, including_parent=True) -> InternalOperationResult:
        try:
            parent = psutil.Process(pid)
        except Exception as e:
            self.logger.error(str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, str(e))

        for child in parent.children(recursive=True):
            try:
                child.kill()
            except Exception as e:
                self.logger.error('Can\'t kill process with pid %s (subprocess of %s) : %s', child.pid, pid, str(e))
        if including_parent:
            try:
                parent.kill()
            except Exception as e:
                self.logger.error('Can\'t kill process with pid %s: %s', parent.pid, str(e))
                return InternalOperationResult(ExecutionStatus.FATAL_ERROR, str(e))

        return InternalOperationResult(ExecutionStatus.SUCCESS)

    def get_free_disk_space(self, path: str) -> (InternalOperationResult, int):
        """Returns free disk capacity in bytes."""

        try:
            capacity = psutil.disk_usage(path=path).free
            return InternalOperationResult(ExecutionStatus.SUCCESS), capacity
        except Exception as e:
            self.logger.warning('Can\'t get information about disk free space: %s', str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, str(e)), None

    def get_storage_capacity(self, path: str) -> (InternalOperationResult, int):
        """Returns total disk capacity in byted."""

        try:
            capacity = psutil.disk_usage(path=path).total
            return InternalOperationResult(ExecutionStatus.SUCCESS), capacity
        except Exception as e:
            self.logger.warning('Can\'t get information about total disk capacity: %s', str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, str(e)), None