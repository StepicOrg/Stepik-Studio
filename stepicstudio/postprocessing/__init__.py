from stepicstudio.models import SubStep
from stepicstudio.postprocessing.raw_cut import RawCutter
from stepicstudio.postprocessing.video_sync import VideoSynchronizer


def synchronize_videos(path_1, path_2):
    synchronizer = VideoSynchronizer()
    synchronizer.sync(path_1, path_2)


def start_subtep_montage(substep_id):
    substep = SubStep.objects.get(id=substep_id)
    cutter = RawCutter()
    cutter.raw_cut_async(substep)
