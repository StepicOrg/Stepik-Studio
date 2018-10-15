from stepicstudio.postprocessing.raw_cut import RawCutter
from stepicstudio.postprocessing.video_sync import VideoSynchronizer


def synchronize_videos(path_1, path_2):
    synchronizer = VideoSynchronizer()
    synchronizer.sync(path_1, path_2)


def start_subtep_montage(substep_id):
    cutter = RawCutter()
    cutter.raw_cut_async(substep_id)


def start_step_montage(step_id):
    cutter = RawCutter()
    cutter.raw_cut_step_async(step_id)


def start_lesson_montage(lesson_id):
    print(lesson_id)
    cutter = RawCutter()
    cutter.raw_cut_lesson_async(lesson_id)
