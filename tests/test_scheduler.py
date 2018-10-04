import datetime
import time

from django.test import TestCase

from stepicstudio.scheduling.task_manager import TaskManager


class TestScheduler(TestCase):
    def test(self):

        # очередь, задачи из которой будут исполнятся в заданное время.
        time_ = datetime.datetime.now() + datetime.timedelta(seconds=5)
        manager = TaskManager(time_.timestamp())
        print('debug 1')
        manager.put_task(print, ['Hi!'])
        print('debug 2')
        time.sleep(10)
        # time_ = datetime.datetime.now() + datetime.timedelta(seconds=5)
        # manager.put_task(print, ['Hi2!'], time_.timestamp())
