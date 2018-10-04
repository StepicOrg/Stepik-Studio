import sched
import time
import threading
from queue import *

from singleton_decorator import singleton


@singleton
class TaskManager(object):
    def __init__(self, datetime_):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.queue = Queue()
        self.datetime = datetime_
        threading.Thread(target=self.__init_sched()).run()
        # self.scheduler.run()

    def __init_sched(self):
        self.scheduler.enterabs(self.datetime, 1, self.__execute_all)
        self.scheduler.run()

    def put_task(self, job: callable, args: list):
        task = ScheduledTask(job, args)
        self.queue.put(task)
        print('put task: {}'.format(self.queue.qsize()))
        # job_to_run = self.queue.get()
        # job_to_run.callable_job(job_to_run.args)
        # self.scheduler.enterabs(datetime_, 1, job_to_run.callable_job, job_to_run.args)
        # self.scheduler.run()

    def __execute_all(self):
        print('qwe')
        print(self.queue.qsize())
        while not self.queue.empty():
            print('Hi not empy')
            task = self.queue.get()
            task.callable_job(task.args)


class ScheduledTask(object):
    def __init__(self, callable_job: callable, *args):
        self.callable_job = callable_job
        self.args = args
