import logging
import os

from django.conf import settings

from stepicstudio.const import MP4_EXTENSION, TS_EXTENSION
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class PostprocessorInterface(object):
    """The handlers included in SERVER_POSTPROCESSING_PIPE is applied to each record"""

    def process(self, path: str, filename: str) -> (str, str):
        """Handle .TS videofile.

        :param path:
            path to the directory containing target file.

        :param filename:
            name of the target videofile.

        :return:
            path and filename of file which is result of handling.
            If at least one of returned values is None,
            then next handler takes previous parameters (:param path and :param filename).
        """
        pass


class TSConverter(PostprocessorInterface):
    def __init__(self):
        self.fs_client = FileSystemClient()
        self.logger = logging.getLogger('stepic_studio.postprocessing.TSConverter')

    def process(self, path: str, filename: str) -> (str, str):
        new_filename = os.path.splitext(filename)[0] + MP4_EXTENSION  # change file extension from .TS to .mp4

        source_file = os.path.join(path, filename)
        target_file = os.path.join(path, new_filename)

        reencode_command = settings.FFMPEG_PATH + ' ' + \
                           settings.CAMERA_REENCODE_TEMPLATE.format(source_file, target_file)

        result, _ = self.fs_client.execute_command(reencode_command)

        if result.status is ExecutionStatus.SUCCESS:
            self.logger.info('Successfully start converting TS to mp4 (FFMPEG command: %s)', reencode_command)
        else:
            self.logger.error('Converting failed: %s; FFMPEG command: %s', result.message, reencode_command)
        return path, new_filename


class FileRemover(PostprocessorInterface):
    def __init__(self):
        self.fs_client = FileSystemClient()
        self.logger = logging.getLogger(__name__)

    def process(self, path: str, filename: str) -> (str, str):
        file_to_remove = os.path.splitext(filename)[0] + TS_EXTENSION
        path = os.path.join(path, file_to_remove)
        if not os.path.isfile(path):
            self.logger.warning('Removing .TS file failed: file %s is not valid.', path)
            return path, filename

        remove_status = self.fs_client.remove_file(path)

        if remove_status.status is not ExecutionStatus.SUCCESS:
            self.logger.error('Removing file %s failed: %s', path, remove_status.message)

        return path, filename
