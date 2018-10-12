import os

from django.test import TestCase

from stepicstudio.const import SYNC_LABEL, MP4_EXTENSION
from stepicstudio.postprocessing.raw_cut import RawCutter

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'


class TestRawCut(TestCase, RawCutter):
    def test_should_get_target_files_by_priority(self):
        filenames = ['test.mp4', 'test.mkv', 'test_sync.mp4']
        labels = ['sync', 'mp4', 'mkv']
        target = self._get_target_by_priority(filenames, labels)
        self.assertEqual(target, filenames[-1])

        target = self._get_target_by_priority(filenames, labels[1:])
        self.assertEqual(target, filenames[0])

        target = self._get_target_by_priority(filenames[:-1], labels)
        self.assertEqual(target, filenames[0])

        filenames = ['1', '2', '3']
        target = self._get_target_by_priority(filenames, labels)
        self.assertEqual(target, None)

    def test_should_get_few_target(self):
        test_cutter = RawCutter()
        test_path = 'D:\\STEPIKSTUDIO\\TESTER\\test_course\\test_n_\\step_n_\\Step2from145'

        screen, prof = test_cutter._get_target_files(test_path)
        print(screen)
        print(prof)
        self.assertTrue(SYNC_LABEL in screen)
        self.assertTrue(MP4_EXTENSION in prof)
