import sched
import time
from datetime import datetime

from singleton_decorator import singleton


@singleton
class TaskManager(object):
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # self.scheduler.run()

    def put_task(self, action, args, datetime_, priority=1):
        # time = datetime()
        self.scheduler.enterabs(datetime_, priority, action, args)
        self.scheduler.run()
