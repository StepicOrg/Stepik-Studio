import logging

from django.conf import settings

from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections.tablet_client import TabletClient

logger = logging.getLogger(__name__)


def get_full_linux_path(substep):
    return settings.LINUX_DIR + substep.os_tablet_path


def get_full_linux_step_path(step):
    return settings.LINUX_DIR + step.tablet_path


def get_full_linux_lesson_path(lesson):
    return settings.LINUX_DIR + lesson.tablet_path


def delete_tablet_substep_files(substep) -> InternalOperationResult:
    client = TabletClient()
    try:
        folder_path = get_full_linux_path(substep)
    except Exception as e:
        logger.warning('Can\'t get tablet path to substep: %s', e)
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, e)

    status, _ = client.delete_folder(folder_path)
    client.close()
    return status


def delete_tablet_step_files(step):
    try:
        client = TabletClient()
        client.delete_folder_recursively(get_full_linux_step_path(step))
        client.close()
        return True
    except Exception as e:
        logger.warning('Failed to remove step %s from tablet (id: %s): %s', step.name, step.id, e)
        return False


def delete_tablet_lesson_files(lesson):
    try:
        client = TabletClient()
        client.delete_folder_recursively(get_full_linux_lesson_path(lesson))
        client.close()
        return True
    except Exception as e:
        logger.warning('Failed to remove lesson %s from tablet (id: %s): %s', lesson.name, lesson.id, e)
        return False
