import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from singleton_decorator import singleton
from tzlocal import get_localzone

logging.getLogger('apscheduler').setLevel(logging.WARNING)


@singleton
class TaskManager(object):
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=get_localzone())
        if settings.PERSISTENT_SCHEDULED_TASKS is True:
            user = settings.DATABASES['default']['USER']
            passsword = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            url = 'postgresql://' + user + ':' + passsword + '@' + host
            self.scheduler.add_jobstore('sqlalchemy', url=url)
        self.scheduler.start()
        self.__logger = logging.getLogger('stepicstudio.scheduling.tesk_manager')

    def run_while_idle_once_time(self, job: callable, args: list):
        launch_time = self.__get_launch_time()
        trigger = DateTrigger(launch_time, timezone=get_localzone())
        self.scheduler.add_job(job, trigger=trigger, args=args)

        self.__logger.info('New task for scheduled execution: %s. \n '
                           'Current size of tasks queue: %s; \n'
                           'Execution time: %s; \n Current time: %s;',
                           getattr(job, '__name__', repr(job)),
                           self.__current_size() + 1,
                           launch_time,
                           datetime.now(self.scheduler.timezone))

    def run_while_idle_repeatable(self, job: callable, single=True):
        self.__logger.info('New task for scheduled repeatable execution: %s. \n '
                           'Execution time: %s:00 of next day; \n Current time: %s;',
                           getattr(job, '__name__', repr(job)),
                           settings.BACKGROUND_TASKS_START_HOUR,
                           datetime.now(self.scheduler.timezone))

        scheduled = self.scheduler.add_job(job, 'cron', hour=str(settings.BACKGROUND_TASKS_START_HOUR))

        if single is True:
            scheduled.modify(max_instances=1)

    def __get_launch_time(self):
        launch_date = datetime.now() + timedelta(days=1)
        return launch_date.replace(hour=settings.BACKGROUND_TASKS_START_HOUR)

    def __current_size(self):
        return self.scheduler.get_jobs().__len__()
