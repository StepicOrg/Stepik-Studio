import logging
import os
import wave

import numpy as np
from django.conf import settings
from scipy.signal import correlate

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.statuses import ExecutionStatus

CHUNKSIZE = 1000000  # bytes
MIN_DIFF_SEC = 0.01
MAX_DIFF_SEC = 2
SAMPLE_SIZES = {
    1: np.byte,
    2: np.int16,
    4: np.int32
}
TEMP_AUDIO_FREQUENCY = 48000

logger = logging.getLogger(__name__)


def get_sync_offset(substep_obj):
    screencast_audio = extract_audio(substep_obj.os_screencast_path)
    prof_audio = extract_audio(substep_obj.os_path)

    wf_prof = wave.open(screencast_audio, 'r')
    wf_screencast = wave.open(prof_audio, 'r')

    diff_sec = get_seconds_diff(wf_screencast, wf_prof)

    wf_prof.close()
    wf_screencast.close()

    FileSystemClient.remove_file(screencast_audio)
    FileSystemClient.remove_file(prof_audio)

    if abs(diff_sec) < MIN_DIFF_SEC or abs(diff_sec) > MAX_DIFF_SEC:
        logger.info('Difference in start times is out of range [%s, %s]; Value: %s; Target substep: %s',
                    MIN_DIFF_SEC, MAX_DIFF_SEC, abs(diff_sec), substep_obj.name)
        return 0

    logger.info('Difference in start times: %s; Empty frames added to %s; Target substep: %s',
                diff_sec, substep_obj.os_path if diff_sec < 0.0 else substep_obj.os_screencast_path, substep_obj.name)

    return diff_sec


def extract_audio(video_path):
    audio_output = os.path.splitext(video_path)[0] + '.wav'

    extract_result = FileSystemClient.execute_command_sync([settings.FFMPEG_PATH, '-y',
                                                            '-i', video_path, '-vn',
                                                            '-acodec', '-pcm_s24le',
                                                            '-ac', '2',
                                                            '-ar', str(TEMP_AUDIO_FREQUENCY),
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

    string_size_1 = SAMPLE_SIZES[wf_audio_1.getnchannels() * wf_audio_1.getsampwidth()]
    string_size_2 = SAMPLE_SIZES[wf_audio_2.getnchannels() * wf_audio_2.getsampwidth()]

    frames_1 = np.fromstring(frames_1, string_size_1)
    frames_2 = np.fromstring(frames_2, string_size_2)

    frames_1 = normalize_signal(frames_1)
    frames_2 = normalize_signal(frames_2)

    corr = correlate(frames_1, frames_2)
    lag = np.argmax(corr)

    return lag - frames_2.size


def get_seconds_diff(wf_audio_1, wf_audio_2) -> float:
    return frames_to_seconds(get_frames_diff(wf_audio_1, wf_audio_2),
                             TEMP_AUDIO_FREQUENCY)
