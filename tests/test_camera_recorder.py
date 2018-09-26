import time
from django.test import TestCase
from stepicstudio.video_recorders.camera_recorder import ServerCameraRecorder
import os

from stepicstudio.operationsstatuses.statuses import ExecutionStatus

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'

"""Functional tests.
Needs delays between starts to free up video device.
"""


class TestCameraRecorder(TestCase):
    def setUp(self):
        self.output_file = 'test_record.TS'
        self.path = 'C:\\Development\\Tests'

    def test_should_successfully_start_and_stop_record(self):
        time.sleep(2)
        cam_recorder = ServerCameraRecorder()
        start_result = cam_recorder.start_recording(self.path, self.output_file)
        self.assertTrue(cam_recorder.is_active())
        self.assertTrue(start_result.status is ExecutionStatus.SUCCESS)
        time.sleep(5)
        stop_result = cam_recorder.stop_recording()
        self.assertTrue(stop_result.status is ExecutionStatus.SUCCESS)
        self.assertFalse(cam_recorder.is_active())

    def test_should_fail_on_start_when_record_is_active(self):
        time.sleep(2)
        cam_recorder = ServerCameraRecorder()
        start_result = cam_recorder.start_recording(self.path, self.output_file)
        self.assertTrue(cam_recorder.is_active())
        self.assertTrue(start_result.status is ExecutionStatus.SUCCESS)

        time.sleep(2)
        start_result = cam_recorder.start_recording(self.path, self.output_file)
        self.assertTrue(start_result.status is ExecutionStatus.FATAL_ERROR)

        time.sleep(2)
        stop_result = cam_recorder.stop_recording()
        self.assertTrue(stop_result.status is ExecutionStatus.SUCCESS)
        self.assertFalse(cam_recorder.is_active())

    def test_should_fail_on_stop_non_existing_record(self):
        cam_recorder = ServerCameraRecorder()

        stop_result = cam_recorder.stop_recording()

        self.assertTrue(stop_result.status is ExecutionStatus.FATAL_ERROR)
