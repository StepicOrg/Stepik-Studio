import json

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult

SCREENCASTS_LABEL = 'screen'
CAMERA_RECORDINGS_LABEL = 'prof'
BASE_PATH_LABEL = 'base_path'
PPRO_TEMPLATES_PATH_LABEL = 'templates_path'


class PremiereExporter(object):
    def __init__(self):
        self.fs_client = FileSystemClient()

    def export_to_pproj(self, step_object) -> InternalOperationResult:
        screen_files = []
        prof_files = []
        for substep in SubStep.objects.filter(from_step=step_object.id):
            if substep.is_videos_ok:
                screen_files.append(substep.screencast_name)
                prof_files.append(substep.camera_recording_name)


        pass

    def params_to_json(self, base_path, templates_path, screen_files, prof_files):
        return json.dumps({BASE_PATH_LABEL: base_path,
                           PPRO_TEMPLATES_PATH_LABEL: templates_path,
                           CAMERA_RECORDINGS_LABEL: prof_files,
                           SCREENCASTS_LABEL: screen_files})
