from django.apps import AppConfig

from stepicstudio.scheduling.task_manager import TaskManager
from stepicstudio.ssh_connections.garbage_collecting import collect_garbage


class StepikStudioConfig(AppConfig):
    name = 'stepicstudio'

    def ready(self):
        task_manager = TaskManager()
        task_manager.run_while_idle_repeatable(collect_garbage)

