import logging
import os
import wave

import numpy as np
from django.conf import settings
from scipy.signal import correlate

from stepicstudio.const import SYNC_LABEL
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus

CHUNKSIZE = 10000  # bytes
MIN_DIFF = 0.03

logger = logging.getLogger(__name__)


def sync(substep_obj):
    screencast_audio = extract_audio(substep_obj.os_screencast_path)
    prof_audio = extract_audio(substep_obj.os_path)

    wf_prof = wave.open(screencast_audio, 'r')
    wf_screencast = wave.open(prof_audio, 'r')

    diff_sec = get_seconds_diff(wf_prof, wf_screencast)

    if diff_sec - MIN_DIFF > 0:
        add_empty_frames(substep_obj.os_path, diff_sec)
    elif diff_sec + MIN_DIFF < 0:
        add_empty_frames(substep_obj.os_screencast_path, abs(diff_sec))
    else:
        logger.info('Video synchronizing: no need to be synchronized')
        return InternalOperationResult(ExecutionStatus.SUCCESS)

    wf_prof.close()
    wf_screencast.close()


def extract_audio(video_path):
    audio_output = os.path.splitext(video_path)[0] + '.wav'

    extract_result = FileSystemClient.execute_command_sync([settings.FFMPEG_PATH, '-y',
                                                            '-i', video_path, '-vn', '-ac', '1',
                                                            '-f', 'wav', audio_output])

    if extract_result.status is not ExecutionStatus.SUCCESS:
        raise Exception(extract_result.message)

    return audio_output


def frames_to_seconds(frames: int, frequency: int) -> float:
    return frames / frequency


def normalize_signal(signal):
    """
    Normalize signal to [-1, 1] range.
    """
    return signal / np.amax(signal)


def get_frames_diff(wf_audio_1, wf_audio_2) -> int:
    frames_1 = wf_audio_1.readframes(CHUNKSIZE)
    frames_2 = wf_audio_2.readframes(CHUNKSIZE)

    string_size_1 = wf_audio_1.getnchannels() * wf_audio_1.getsampwidth()
    string_size_2 = wf_audio_2.getnchannels() * wf_audio_2.getsampwidth()

    frames_1 = np.fromstring(frames_1, string_size_1)
    frames_2 = np.fromstring(frames_2, string_size_2)

    frames_1 = normalize_signal(frames_1)
    frames_2 = normalize_signal(frames_2)

    corr = correlate(frames_1, frames_2)
    lag = np.argmax(corr)

    return lag - frames_2.size


def get_seconds_diff(wf_audio_1, wf_audio_2) -> float:
    return frames_to_seconds(get_frames_diff(wf_audio_1, wf_audio_2),
                             wf_audio_1.get_framerate())


def add_empty_frames(path, duration):
    splitted_path = os.path.splitext(path)
    new_path = splitted_path[0] + SYNC_LABEL + splitted_path[1]
    duration = '%.3f' % duration
    command = settings.FFMPEG_PATH + ' ' + settings.VIDEO_OFFSET_TEMPLATE.format(duration, path, new_path)

    status = FileSystemClient.execute_command_sync(command)

    if status.status is not ExecutionStatus.SUCCESS:
        raise Exception(status.message)
