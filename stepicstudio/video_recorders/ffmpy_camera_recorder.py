import threading
import ffmpy
from django.conf import settings
import logging


# Experimental implementation of camera recorder

class CameraRecorder(object):
    def __init__(self, output_filename: str):
        self.__logger = logging.getLogger('stepic_studio.FileSystemOperations.camera_recorder')
        self.__process = None
        self.__ffmpeg = ffmpy.FFmpeg(executable=settings.FFMPEG_PATH,
                                     global_options=settings.FFMPEG_COMM_PART,
                                     outputs={output_filename: None})

    def __execute(self):
        try:
            self.__ffmpeg.run()
        except ffmpy.FFRuntimeError as e:
            # run() will raise exception with exit code 255 when thread is interrupted - it's OK
            if e.exit_code and e.exit_code != 255:
                self.__logger.error('Problems with ffmpeg: %s', str(e))
                raise e

    def start_recording(self):
        self.__process = threading.Thread(target=self.__execute)
        self.__process.start()

    def stop_recording(self):
        self.__ffmpeg.process.terminate()

    def __str__(self):
        return self.__ffmpeg.cmd
