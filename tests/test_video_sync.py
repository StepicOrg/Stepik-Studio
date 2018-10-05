from django.test import TestCase

from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.postprocessing.video_sync import VideoSynchronizer


class TestSynchronization(TestCase):
    def test_video_sync(self):
        path_1 = 'D:\\STEPIKSTUDIO\\TESTER\\test_course\\test_2\\step_2\\Step18from137\\Step18from137_Screen.mkv'
        path_2 = 'D:\\STEPIKSTUDIO\\TESTER\\test_course\\test_2\\step_2\\Step18from137\\Step18from137_Professor.TS'
        sync = VideoSynchronizer()
        status = sync.sync(path_2, path_1)
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
