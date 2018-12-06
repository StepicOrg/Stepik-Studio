import logging

from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections.tablet_client import TabletClient

logger = logging.getLogger(__name__)


def delete_tablet_substep_files(substep) -> InternalOperationResult:
    client = TabletClient()
    status = client.delete_file(substep.os_tablet_path)
    client.close()
    return status


def delete_tablet_step_files(step) -> InternalOperationResult:
    try:
        client = TabletClient()
        client.delete_folder_recursively(step.tablet_path)
        client.close()
        return InternalOperationResult(ExecutionStatus.SUCCESS)
    except Exception as e:
        logger.warning('Failed to remove step %s from tablet (id: %s): %s', step.name, step.id, e)
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR)


def delete_tablet_lesson_files(lesson) -> InternalOperationResult:
    try:
        client = TabletClient()
        client.delete_folder_recursively(lesson.tablet_path)
        client.close()
        return InternalOperationResult(ExecutionStatus.SUCCESS)
    except Exception as e:
        logger.warning('Failed to remove lesson %s from tablet (id: %s): %s', lesson.name, lesson.id, e)
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR)
