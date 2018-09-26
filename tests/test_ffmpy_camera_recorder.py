import time
from django.test import TestCase
from stepicstudio.VideoRecorder.camera_recorder import ServerCameraRecorder
import os

from stepicstudio.operationsstatuses.statuses import ExecutionStatus

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'


# functional tests

class TestCameraRecorder(TestCase):
    def test_should_start_and_stop_record(self):
        output_file = 'test_record.TS'
        path = 'C:\\Development\\Tests'
        cam_recorder = ServerCameraRecorder()
        start_result = cam_recorder.start_recording(path, output_file)
        self.assertTrue(cam_recorder.is_active())
        self.assertTrue(start_result.status is ExecutionStatus.SUCCESS)
        time.sleep(5)
        stop_result = cam_recorder.stop_recording()
        self.assertTrue(stop_result.status is ExecutionStatus.SUCCESS)
        self.assertFalse(cam_recorder.is_active())
