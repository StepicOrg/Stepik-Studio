import logging
from multiprocessing import Queue

from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from singleton_decorator import singleton

logging.getLogger('apscheduler').setLevel(logging.WARNING)


@singleton
class TaskManager(object):
    def __init__(self):
        self.scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
        self.scheduler.start()
        self.queue = Queue()
        self.__logger = logging.getLogger('stepicstudio.scheduling.tesk_manager')
        self.scheduler.add_job(self.__execute_jobs, 'cron', hour=settings.BACKGROUND_TASKS_START_HOUR)
        #  sched.add_job(my_job, trigger='cron', hour='22', minute='30')

    def run_while_idle_once_time(self, job: callable):
        self.__logger.info('New task for once time idle execution! Current queue size: %s tasks.', self.queue.qsize())
        self.queue.put(job)

    def repeat_while_idle(self, job: callable):
        self.scheduler.add_job(job, 'cron', second='*')

    def __execute_jobs(self):
        try:
            while not self.queue.empty():
                task = self.queue.get()
                task()
        except Exception as e:
            self.__logger.error('Error while execute queued tasks: %s', e)
