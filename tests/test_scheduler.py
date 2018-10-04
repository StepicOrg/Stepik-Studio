import datetime
import time

from django.test import TestCase

from stepicstudio.scheduling.task_manager import TaskManager


class TestScheduler(TestCase):
    def test(self):
        manager = TaskManager()
        # очередь, задачи из которой будут исполнятся в заданное время.
        time_ = datetime.datetime.now() + datetime.timedelta(seconds=5)
        manager.put_task(print, ['Hi!'], time_.timestamp())
        time.sleep(10)
        # time_ = datetime.datetime.now() + datetime.timedelta(seconds=5)
        # manager.put_task(print, ['Hi2!'], time_.timestamp())
