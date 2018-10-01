import os
import logging
import subprocess

from django.conf import settings
from stepicstudio.FileSystemOperations.file_system_client import FileSystemClient
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus


class VideoSynchronizer(object):
    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__logger = logging.getLogger('stepic_studio.postprocessing.VideSynchronizer')

    def sync(self, path_1, path_2):
        if not self.__fs_client.validate_file(path_1) or \
                not self.__fs_client.validate_file(path_2):
            self.__logger.error('Can\'t synchronize invalid videos (%s; %s)', path_1, path_2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        try:
            audio_1 = self.__extract_audio(path_1)
            audio_2 = self.__extract_audio(path_2)
        except Exception as e:
            self.__logger.error('Can\'t extract audio from %s, %s: %s', path_1, path_2, str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        try:
            duration_1 = self.__get_silence_duration(audio_1)
            duration_2 = self.__get_silence_duration(audio_2)
        except Exception as e:
            self.__logger.exception('Can\'t get silence duration of %s, %s: %s', audio_1, audio_2, str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        print('First output: {}'.format(duration_1))
        print('Second output: {}'.format(duration_2))

    def __extract_audio(self, video_path):
        wo_extension = os.path.splitext(video_path)[0]
        audio_output = wo_extension + '.wav'
        extract_result = self.__fs_client.execute_command_sync(
            [settings.FFMPEG_PATH, '-y', '-i', video_path, '-vn', '-ac', '1', '-f', 'wav', audio_output])

        if extract_result.status is not ExecutionStatus.SUCCESS:
            raise Exception(extract_result.message)
        else:
            return audio_output

    def __get_silence_duration(self, audio_path, noise_level='-25dB', min_duration='0.1'):
        command = settings.FFMPEG_PATH + ' ' + settings.SILENCE_DETECT_TEMPLATE.format(audio_path, noise_level,
                                                                                       min_duration)

        status, output = self.__fs_client.exec_and_get_output(command, stderr=subprocess.STDOUT)
        if status.status is not ExecutionStatus.SUCCESS:
            raise Exception(status.message)

        info = self.__extract_silence_info(output)

        try:
            self.__info_validate(info)
            return info['silence_duration']
        except Exception as e:
            raise e

    def __info_validate(self, info: dict):
        try:
            start_time = float(info['silence_start'])
            if start_time > 0:
                raise Exception('Start of audio doesn\'t contain silence')
        except Exception as e:
            raise e

    # extract info about first silent part
    def __extract_silence_info(self, raw_info) -> dict:
        result = []

        for row in raw_info.decode('UTF-8').split('\n'):
            if 'silencedetect' in row:
                result.append(row)

        keys = []
        digits = []
        for elem in result:
            for s in elem.split():
                if 'silence_' in s:
                    keys.append(s[:-1])  # pass ':' character
                else:
                    try:
                        digits.append(float(s))
                    except:
                        pass

        dictionary = {}

        for idx, key in enumerate(keys):
            if key not in dictionary:
                dictionary[key] = digits[idx]

        return dictionary
