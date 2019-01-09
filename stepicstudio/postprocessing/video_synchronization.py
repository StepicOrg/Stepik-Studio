import logging
import os
import wave

import numpy as np
from django.conf import settings
from scipy.signal import correlate

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.statuses import ExecutionStatus

CHUNKSIZE = 1000000
MIN_DIFF_SEC = 0.01
MAX_DIFF_SEC = 2
SAMPLE_SIZES = {
    1: np.byte,
    2: np.int16,
    4: np.int32
}
TEMP_AUDIO_FREQUENCY = 48000

logger = logging.getLogger(__name__)


class ClosableWaveExtractor(object):
    def __init__(self, video_path):
        self.video_path = video_path

    def __enter__(self):
        self.audio_path = os.path.splitext(self.video_path)[0] + '.wav'

        extract_result = FileSystemClient.execute_command_sync([settings.FFMPEG_PATH, '-y',
                                                                '-i', self.video_path, '-vn',
                                                                '-ac', '1',
                                                                '-ar', str(TEMP_AUDIO_FREQUENCY),
                                                                '-f', 'wav', self.audio_path])

        if extract_result.status is not ExecutionStatus.SUCCESS:
            raise Exception(extract_result.message)

        self.wave_form = wave.open(self.audio_path, 'r')

        return self.wave_form

    def __exit__(self, *exc_info):
        self.wave_form.close()
        FileSystemClient.remove_file(self.audio_path)


def get_sync_offset(substep_obj):
    with ClosableWaveExtractor(substep_obj.os_screencast_path) as wf_screencast, \
            ClosableWaveExtractor(substep_obj.os_path) as wf_prof:
        diff_sec = get_seconds_diff(wf_screencast, wf_prof)

    if abs(diff_sec) < MIN_DIFF_SEC or abs(diff_sec) > MAX_DIFF_SEC:
        logger.info('Difference in start times is out of range [%s, %s]; Value: %s; Target substep: %s',
                    MIN_DIFF_SEC, MAX_DIFF_SEC, abs(diff_sec), substep_obj.name)
        return 0

    logger.info('Difference in start times: %s; Empty frames added to %s; Target substep: %s',
                diff_sec, substep_obj.os_path if diff_sec < 0.0 else substep_obj.os_screencast_path, substep_obj.name)

    return diff_sec


def frames_to_seconds(frames: int, frequency: int) -> float:
    return frames / frequency


def normalize_signal(signal):
    """
    Normalize signal to [-1, 1] range.
    """
    return signal / np.amax(signal)


def get_frames_diff(wf_audio_1, wf_audio_2) -> int:
    data_size = max(wf_audio_1.getnframes(), wf_audio_2.getnframes()) * \
                wf_audio_1.getnchannels() * \
                wf_audio_1.getsampwidth()

    # use last frames to avoid .wav delay due to FFMPEG issue
    frames_1 = wf_audio_1.readframes(data_size)[-CHUNKSIZE:]
    frames_2 = wf_audio_2.readframes(data_size)[-CHUNKSIZE:]

    # parameters of wav files must be the same (according to FFMPEG parameters)
    string_size = SAMPLE_SIZES[wf_audio_1.getnchannels() * wf_audio_1.getsampwidth()]

    frames_1 = np.fromstring(frames_1, string_size)
    frames_2 = np.fromstring(frames_2, string_size)

    frames_1 = normalize_signal(frames_1)
    frames_2 = normalize_signal(frames_2)

    corr = correlate(frames_1, frames_2)
    lag = np.argmax(corr)

    return lag - frames_2.size


def get_seconds_diff(wf_audio_1, wf_audio_2) -> float:
    return frames_to_seconds(get_frames_diff(wf_audio_1, wf_audio_2),
                             TEMP_AUDIO_FREQUENCY)
