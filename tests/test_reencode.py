from django.test import TestCase
from stepicstudio.FileSystemOperations.action import reencode_to_mp4
from stepicstudio.operationsstatuses.statuses import ExecutionStatus
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'


# functional tests

class TestReencodeMethod(TestCase):
    def test_reencode_should_be_successful(self):
        path = 'D:\\STEPIKSTUDIO\\TESTER\\testing\\1234\\1234\\Step14from127'
        filename = 'Step14from127_Professor.TS'
        result = reencode_to_mp4(path, filename)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)

    def test_reencode_should_fail_with_no_such_file(self):
        path = 'random_non_existing_file'
        file = 'non_existing_file'
        result = reencode_to_mp4(path, file)
        self.assertEqual(result.status, ExecutionStatus.FATAL_ERROR)
