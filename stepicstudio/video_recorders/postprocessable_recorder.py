import logging
import os

from django.utils.module_loading import import_string

from stepicstudio.FileSystemOperations.file_system_client import FileSystemClient


class PostprocessableRecorder(object):
    def __init__(self):
        self.__postprocessor_pipe = []
        self.__logger = logging.getLogger('stepic_studio.video_recorders.postprocessable_recorder')
        self.__fs_client = FileSystemClient()

    def _load_postprocessing_pipe(self, pipe: set):
        for path in pipe:
            pp_class = import_string(path)
            try:
                pp_instance = pp_class()
            except Exception:
                self.__logger.warning('Can\'t load %s for postprocessing', pp_class)
                continue

            if hasattr(pp_instance, 'process'):
                self.__postprocessor_pipe.append(pp_instance.process)

    def _apply_pipe(self, path: str, filename: str):
        if path is None or filename is None:
            return
        source_file = os.path.join(path, filename)

        if not self.__fs_client.validate_file(source_file):
            self.__logger.error('Can\'t apply postprocessing pipe to %s: it\'s not a file', source_file)
            return
        result_path = path
        result_file = filename
        for processor in self.__postprocessor_pipe:
            try:
                new_path, new_file = processor(result_path, result_file)
                if new_file is not None and new_path is not None:
                    result_file = new_file
                    result_path = new_path
            except Exception as e:
                self.__logger.warning('Can\'t apply %s to record result: %s', processor, str(e))
