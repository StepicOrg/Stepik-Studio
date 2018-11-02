import logging
import os
import subprocess

from django.conf import settings

from stepicstudio.const import SYNC_LABEL
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class VideoSynchronizer(object):
    """Video synchronization via durations of silence at the start of videos"""

    def __init__(self):
        self.__fs_client = FileSystemClient()
        self.__logger = logging.getLogger('stepic_studio.postprocessing.VideSynchronizer')

        self.__max_diff = 2  # seconds
        self.__min_diff = 0.1

        self.__camera_noise_tolerance = '-11.5dB'
        self.__tablet_noise_tolerance = '-12dB'
        self.__min_silence_duration = 0.001

    def sync(self, screen_path, camera_path) -> InternalOperationResult:
        screen_path = os.path.splitext(screen_path)[0] + '.mp4'
        camera_path = os.path.splitext(camera_path)[0] + '.mp4'
        if not os.path.isfile(screen_path) or not os.path.isfile(camera_path):
            self.__logger.warning('Invalid paths to videos: (%s; %s)', screen_path, camera_path)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        try:
            duration_1 = self.__get_silence_duration(screen_path, self.__tablet_noise_tolerance,
                                                     self.__min_silence_duration)
            duration_2 = self.__get_silence_duration(camera_path, self.__camera_noise_tolerance,
                                                     self.__min_silence_duration)
        except Exception as e:
            self.__logger.warning('Can\'t get silence duration of %s, %s.', screen_path, camera_path)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        longer = ''
        try:
            silence_diff = self.__get_valid_silence_diff(duration_1, duration_2)

            if silence_diff == 0:
                self.__logger.info('Video synchronizing: no need to be synchronized, silence difference < %ssec.',
                                   self.__min_diff)
                return InternalOperationResult(ExecutionStatus.SUCCESS)

            if silence_diff > 0:
                longer = screen_path
                self.__add_empty_frames(camera_path, silence_diff)
            elif silence_diff < 0:
                longer = camera_path
                self.__add_empty_frames(screen_path, abs(silence_diff))
        except Exception as e:
            self.__logger.warning('Invalide difference: %s', e)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        self.__logger.info('Videos successfully synchronized (difference: %s sec.; longer silence in  %s; '
                           'silence duration of %s - %s sec.; silence duration of %s - %s sec.)',
                           '%.3f' % silence_diff, longer, screen_path, duration_1, camera_path, duration_2)

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

        if abs(val_1 - val_2) < self.__min_diff:
            return 0

        return val_1 - val_2

    def __add_empty_frames(self, path, duration):
        splitted_path = os.path.splitext(path)
        new_path = splitted_path[0] + SYNC_LABEL + splitted_path[1]
        duration = '%.3f' % duration
        command = settings.FFMPEG_PATH + ' ' + settings.VIDEO_OFFSET_TEMPLATE.format(duration, path, new_path)

        status = self.__fs_client.execute_command_sync(command)

        if status.status is not ExecutionStatus.SUCCESS:
            raise Exception(status.message)
