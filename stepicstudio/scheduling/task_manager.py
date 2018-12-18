import logging
from datetime import datetime, timedelta

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from singleton_decorator import singleton
from tzlocal import get_localzone

logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# wait for resheduling missed tasks:
MISFIRE_GRACE_SECONDS = 60 * 60 * 24 * 2  # 2 days in seconds
THREAD_POOL_SIZE = 3


@singleton
class TaskManager(object):
    def __init__(self):
        executors = {'default': ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)}
        self.scheduler = BackgroundScheduler(executors=executors, timezone=get_localzone())
        if settings.PERSISTENT_SCHEDULED_TASKS is True:
            user = settings.DATABASES['default']['USER']
            passsword = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            db_name = settings.DATABASES['default']['NAME']
            url = 'postgresql://' + user + ':' + passsword + '@' + host + '/' + db_name
            self.scheduler.add_jobstore('sqlalchemy', url=url)

        self.__logger = logging.getLogger(__name__)
        self.scheduler.add_listener(self.__exception_listener, EVENT_JOB_ERROR)
        self.scheduler.start()

    def run_once_time(self, job: callable, args):
        launch_time = self.__get_launch_time()
        trigger = DateTrigger(launch_time, timezone=get_localzone())
        self.scheduler.add_job(func=job,
                               trigger=trigger,
                               args=args,
                               misfire_grace_time=MISFIRE_GRACE_SECONDS)

        self.__logger.info('New task for scheduled execution: %s. \n '
                           'Current size of tasks queue: %s; \n'
                           'Execution time: %s; \n Current time: %s;',
                           getattr(job, '__name__', repr(job)),
                           self.__current_size(),
                           launch_time,
                           datetime.now(self.scheduler.timezone))

    def run_with_delay(self, job: callable, args, delay=0):
        self.scheduler.add_job(func=job,
                               trigger='date',
                               next_run_time=datetime.now() + timedelta(seconds=delay),
                               args=args,
                               misfire_grace_time=MISFIRE_GRACE_SECONDS)

    def run_while_idle_repeatable(self, job: callable, single=True):
        if single:
            for task in self.scheduler.get_jobs():
                if job.__name__ in str(task):
                    self.__logger.info('Scheduler already contains task with name \'%s\'.', job.__name__)
                    return

        self.scheduler.add_job(func=job,
                               trigger='cron',
                               hour=settings.BACKGROUND_TASKS_START_HOUR,
                               misfire_grace_time=MISFIRE_GRACE_SECONDS)

        self.__logger.info('New task for scheduled repeatable execution: %s. \n '
                           'Execution time: %s:00 of next day; \n Current time: %s; \n'
                           'Size of scheduler queue: %s tasks.',
                           getattr(job, '__name__', repr(job)),
                           settings.BACKGROUND_TASKS_START_HOUR,
                           datetime.now(self.scheduler.timezone),
                           self.__current_size())

    def remove_all_tasks(self):
        for task in self.scheduler.get_jobs():
            task.remove()

    def __get_launch_time(self):
        launch_date = datetime.now() + timedelta(days=1)
        return launch_date.replace(hour=settings.BACKGROUND_TASKS_START_HOUR)

    def __current_size(self):
        return self.scheduler.get_jobs().__len__()

    def __exception_listener(self, event):
        if event.exception:
            self.__logger.warning('Exception was caught while handle %s: %s', event, event.exception)
