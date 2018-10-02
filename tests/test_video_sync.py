import os
from django.test import TestCase

from stepicstudio.postprocessing.video_sync import VideoSynchronizer


class TestSynchronization(TestCase):
    def test_reencode_should_be_successful(self):
        path_1 = 'C:\\Development\\Tests\\prof.mp4'
        path_2 = 'C:\\Development\\Tests\\screen.mp4'
        sync = VideoSynchronizer()
        sync.sync(path_1, path_2)
