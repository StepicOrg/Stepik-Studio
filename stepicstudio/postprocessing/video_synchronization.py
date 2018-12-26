import os

from django.conf import settings

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.operations_statuses.statuses import ExecutionStatus


def sync(substep_obj):
    screencast_audio = extract_audio(substep_obj.os_screencast_path)
    prof_audio = extract_audio(substep_obj.os_path)


def extract_audio(video_path):
    wo_extension = os.path.splitext(video_path)[0]
    audio_output = wo_extension + '.wav'

    extract_result = FileSystemClient.execute_command_sync([settings.FFMPEG_PATH, '-y',
                                                            '-i', video_path, '-vn', '-ac', '1',
                                                            '-f', 'wav', audio_output])

    if extract_result.status is not ExecutionStatus.SUCCESS:
        raise Exception(extract_result.message)

    return audio_output


def process(audio_1, audio_2, output_file: str):
    self._check_compability(audio_1, audio_2)

    diff = self.get_frames_diff(audio_1, audio_2)

    if diff <= 0:
        source = wave.open(audio_1.path, 'r')
    else:
        source = wave.open(audio_2.path, 'r')

    output = get_output_waveform(output_file,
                                 source.getnchannels(),
                                 source.getsampwidth(),
                                 source.getframerate())

    original = source.readframes(self.chunksize)
    silence = np.zeros(abs(diff), audio_1.get_sample_size())
    silence = np.frombuffer(silence, np.byte)

    output.writeframes(b''.join(silence))

    while original != b'':
        output.writeframes(b''.join(np.frombuffer(original, np.byte)))
        original = source.readframes(self.chunksize)

    source.close()
    output.close()
