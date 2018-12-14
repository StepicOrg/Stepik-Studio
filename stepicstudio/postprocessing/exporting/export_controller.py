from singleton_decorator import singleton

from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.postprocessing.exporting import get_target_course_files, get_target_lesson_files, \
    get_target_step_files, export_obj_to_prproj
from stepicstudio.scheduling.task_manager import TaskManager


@singleton
class PProExportController(object):
    def __init__(self):
        self.current_job = None

    def export(self, db_object, obj_type) -> InternalOperationResult:
        if self.current_job:
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR,
                                           'Only one project may be in exporting process at the same time. '
                                           'Please wait.')

        if obj_type == 'course':
            files_extractor = get_target_course_files
        elif obj_type == 'lesson':
            files_extractor = get_target_lesson_files
        elif obj_type == 'step':
            files_extractor = get_target_step_files
        else:
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR,
                                           'Unsupported type of object: \'{}\''.format(obj_type))

        self.current_job = TaskManager().run_with_delay(export_obj_to_prproj, [db_object, files_extractor], delay=0)

        return export_obj_to_prproj(db_object, files_extractor)
