import os
import time

from django.test import TestCase

from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.video_recorders.tablet_recorder import TabletScreenRecorder

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'

"""Functional tests.
Needs delays between starts to free up video device.
"""


class TestCameraRecorder(TestCase):
    def test_should_successfully_start_and_stop_record(self):
        time.sleep(2)
        recorder = TabletScreenRecorder()
        status = recorder.start_recording('/home/user/VIDEO/STEPICSTUDIO/tester/tests', 'test_1')
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
        time.sleep(4)
        self.assertTrue(recorder.is_active())
        status = recorder.stop_recording()
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
        self.assertFalse(recorder.is_active())

    def test_should_fail_on_repeating_start_or_stop(self):
        time.sleep(1)
        recorder = TabletScreenRecorder()
        status = recorder.start_recording('/home/user/VIDEO/STEPICSTUDIO/tester/tests', 'test_2')
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
        time.sleep(1)

        status = recorder.start_recording('/home/user/VIDEO/STEPICSTUDIO/tester/tests', 'test_2')
        self.assertEqual(status.status, ExecutionStatus.FATAL_ERROR)
        time.sleep(1)

        status = recorder.stop_recording()
        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
        time.sleep(1)
        self.assertFalse(recorder.is_active())

        status = recorder.stop_recording()
        self.assertEqual(status.status, ExecutionStatus.FATAL_ERROR)
