from stepicstudio.postprocessing.video_sync import VideoSynchronizer


def synchronize_videos(path_1, path_2):
    synchronizer = VideoSynchronizer()
    synchronizer.sync(path_1, path_2)