import os

from django.conf import settings
from django.test import TestCase

from stepicstudio.postprocessing.exporting import PremiereExporter



class TestRawCut(TestCase, PremiereExporter):
    def test_should_generate_json_from_files_list(self):
        print(settings.BASE_DIR)
