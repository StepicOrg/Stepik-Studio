import time
from django.test import TestCase
from stepicstudio.video_recorders.ffmpy_camera_recorder import CameraRecorder
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'


# functional tests

class TestCameraRecorder(TestCase):
    def test_should_record_from_camera(self):
        output_file = 'C:\\Development\\Tests\\test_record.TS'
        cam_recorder = CameraRecorder(output_file)
        cam_recorder.start_recording()
        time.sleep(10)
        cam_recorder.stop_recording()