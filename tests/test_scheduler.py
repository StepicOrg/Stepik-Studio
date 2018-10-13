import time
from functools import partial

from django.test import TestCase

from stepicstudio.scheduling.task_manager import TaskManager

n = 0


def func():
    global n
    n += 1
    print('Current value(func): {}'.format(n))


def func2(step):
    global n
    n += step
    print('Current value(func2): {}'.format(n))


class TestScheduler(TestCase):
    def test(self):
        global n
        manager = TaskManager()
        manager.run_while_idle_once_time(func)
        time.sleep(2)
        self.assertEqual(n, 1)
        manager.run_while_idle_once_time(partial(func2, 2))
        time.sleep(5)
        self.assertEqual(n, 3)
        print('End value: {}'.format(n))
