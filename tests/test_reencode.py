from django.test import TestCase
import os

from stepicstudio.postprocessing.postprocessors import TSConverter

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'


# functional tests

class TestReencodeMethod(TestCase):
    def test_reencode_should_be_successful(self):
        converter = TSConverter()
        path = 'D:\\STEPIKSTUDIO\\TESTER\\testing\\1234\\1234\\Step14from127'
        filename = 'Step14from127_Professor.TS'
        converter.process(path, filename)
