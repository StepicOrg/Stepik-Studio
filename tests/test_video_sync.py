from django.test import TestCase

from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.postprocessing.video_sync import VideoSynchronizer


class TestSynchronization(TestCase):
    def test_video_sync(self):
        path_1 = 'C:\\Development\\Tests\\screen.mp4'
        path_2 = 'C:\\Development\\Tests\\prof.mp4'
        sync = VideoSynchronizer()
        status = sync.sync(path_1, path_2)
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
