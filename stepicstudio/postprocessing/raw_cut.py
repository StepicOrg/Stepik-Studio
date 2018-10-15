import logging

import os
from threading import Thread

from django.conf import settings

from stepicstudio.const import SYNC_LABEL, SCREEN_LABEL, PROFESSOR_LABEL, MP4_EXTENSION, MKV_EXTENSION, TS_EXTENSION, \
    RAW_MONTAGE_LABEL
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class RawCutter(object):
    def __init__(self):
        self._fs_client = FileSystemClient()
        self.__logger = logging.getLogger(__name__)
        self.__process = None

    def raw_cut_async(self, substep_id: int):
        try:
            thread = Thread(target=self.raw_cut, args=[substep_id])
            thread.start()
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut asynchronously: %s', e)

    def raw_cut(self, substep_id: int) -> InternalOperationResult:
        substep = SubStep.objects.get(pk=substep_id)

        if substep.automontage_exist:
            return InternalOperationResult(ExecutionStatus.SUCCESS)

        dir_path = substep.dir_path

        if not self._fs_client.is_dir_valid(dir_path):
            self.__logger.warning('Invalid path to substep: %s', dir_path)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        screen, prof = self._get_target_files(dir_path)
        if screen is None or prof is None:
            self.__logger.warning('Can\'t extract videos from dir %s for raw cut.', dir_path)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        screen_full_path = os.path.join(dir_path, screen)
        prof_full_path = os.path.join(dir_path, prof)
        full_output = os.path.join(dir_path, substep.name + RAW_MONTAGE_LABEL + MP4_EXTENSION)

        substep.is_locked = True
        substep.save()
        internal_status = self._internal_raw_cut(screen_full_path, prof_full_path, full_output)
        substep = SubStep.objects.get(pk=substep_id)
        substep.is_locked = False
        substep.save()

        return internal_status

    def raw_cut_step_async(self, step_id: int):
        try:
            substep_ids = SubStep.objects.all().filter(from_step=step_id).values_list('id', flat=True)
            thread = Thread(target=self._internal_raw_cut_step, args=[substep_ids])
            thread.start()
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut_step asynchronously: %s', e)

    def _internal_raw_cut_step(self, substep_ids):
        for id in substep_ids:
            # self.raw_cut(id)
            print(SubStep.objects.all().filter(pk=id).os_path)


    def _internal_raw_cut(self, video_path1: str, video_path2: str, output_path: str) -> InternalOperationResult:
        status_1 = self._fs_client.is_file_valid(video_path1)
        status_2 = self._fs_client.is_file_valid(video_path2)

        if not status_1 or not status_2:
            self.__logger.warning('Can\'t process invalid videos: %s, %s', video_path1, video_path2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        command = settings.FFMPEG_PATH + ' ' + \
                  settings.RAW_CUT_TEMPLATE.format(video_path1, video_path2, output_path)

        status = self._fs_client.execute_command_sync(command)

        if status.status is not ExecutionStatus.SUCCESS:
            return status

    def _cancel(self):
        if self.__process is not None:
            pid = self.__process.pid
            if self._fs_client.is_process_exists(pid):
                self._fs_client.kill_process(pid)
                self.__process = None

    def _get_target_files(self, path):
        filenames = self._fs_client.listdir_files(path)

        screencasts = list(filter(lambda s: SCREEN_LABEL in s, filenames))
        cam_records = list(filter(lambda s: PROFESSOR_LABEL in s, filenames))

        target_screen = self._get_target_by_priority(screencasts, [SYNC_LABEL, MP4_EXTENSION, MKV_EXTENSION])
        target_cam = self._get_target_by_priority(cam_records, [SYNC_LABEL, MP4_EXTENSION, TS_EXTENSION])

        return target_screen, target_cam

    def _get_target_by_priority(self, filenames: list, labels_by_priority: list):
        for label in labels_by_priority:
            for f in filenames:
                if label in f:
                    return f

        return None
