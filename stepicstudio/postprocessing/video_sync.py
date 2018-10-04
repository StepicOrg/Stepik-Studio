import logging
import os
import subprocess

from django.conf import settings

from stepicstudio.FileSystemOperations.file_system_client import FileSystemClient
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus


class VideoSynchronizer(object):
    """Video synchronization via durations of silence at the start of videos"""

    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__logger = logging.getLogger('stepic_studio.postprocessing.VideSynchronizer')

        self.__max_diff = 5  # seconds
        self.__noise_normalization = '-20dB'
        self.__min_duration = 0.1

    def sync(self, path_1, path_2):
        path_1 = os.path.splitext(path_1)[0] + '.mp4'
        path_2 = os.path.splitext(path_2)[0] + '.mp4'
        if not self.__fs_client.validate_file(path_1) or \
                not self.__fs_client.validate_file(path_2):
            self.__logger.error('Can\'t synchronize invalid videos (%s; %s)', path_1, path_2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        try:
            duration_1 = self.__get_silence_duration(path_1, self.__noise_normalization, self.__min_duration)
            duration_2 = self.__get_silence_duration(path_2, self.__noise_normalization, self.__min_duration)
        except Exception as e:
            self.__logger.error('Can\'t get silence duration of %s, %s: %s', path_1, path_2, str(e))
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        longer = ''
        try:
            silence_diff = self.__get_valid_silence_diff(duration_1, duration_2)
            if silence_diff > 0:
                longer = path_1
                self.__add_empty_frames(path_2, silence_diff)
            elif silence_diff < 0:
                longer = path_2
                self.__add_empty_frames(path_1, abs(silence_diff))
        except Exception as e:
            self.__logger.error('Invalide difference: %s', e)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        self.__logger.info('Videos successfully synchronized (difference: %s sec.; longer video: %s; '
                           'silence duration of %s - %s sec.; silence duration of %s - %s sec.)',
                           '%.3f' % silence_diff, longer, path_1, duration_1, path_2, duration_2)

        return InternalOperationResult(ExecutionStatus.SUCCESS)

    def __extract_audio(self, video_path):
        wo_extension = os.path.splitext(video_path)[0]
        audio_output = wo_extension + '.wav'
        extract_result = self.__fs_client.execute_command_sync(
            [settings.FFMPEG_PATH, '-y', '-i', video_path, '-vn', '-ac', '1', '-f', 'wav', audio_output])

        if extract_result.status is not ExecutionStatus.SUCCESS:
            raise Exception(extract_result.message)
        else:
            return audio_output

    def __get_silence_duration(self, audio_path, noise_level='-30dB', min_duration=0.1):
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

    #
    def __get_valid_silence_diff(self, val_1, val_2):
        if abs(val_1 - val_2) > self.__max_diff:
            raise Exception('Silence duration difference exceeds allowable value, difference: {}'
                            .format(abs(val_1 - val_2)))

        return val_1 - val_2

    def __add_empty_frames(self, path, duration):
        splitted_path = os.path.splitext(path)
        new_path = splitted_path[0] + '_synchronized' + splitted_path[1]
        duration = '%.3f' % duration
        command = settings.FFMPEG_PATH + ' ' + settings.VIDEO_OFFSET_TEMPLATE.format(duration, path, new_path)

        status = self.__fs_client.execute_command_sync(command)

        if status.status is not ExecutionStatus.SUCCESS:
            raise Exception(status.message)
