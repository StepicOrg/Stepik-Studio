import logging
import os
from threading import Thread

from django.conf import settings

from stepicstudio.const import MP4_EXTENSION, RAW_CUT_LABEL
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import SubStep, Step
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus


class RawCutter(object):
    def __init__(self):
        self._fs_client = FileSystemClient()
        self.__logger = logging.getLogger(__name__)

    def raw_cut(self, substep_id: int) -> InternalOperationResult:
        substep = SubStep.objects.get(pk=substep_id)

        if substep.automontage_exist:
            return InternalOperationResult(ExecutionStatus.SUCCESS)

        screen_full_path = substep.os_screencast_path
        prof_full_path = substep.os_path

        output_dir = substep.os_automontage_path
        status = self._fs_client.create_recursively(output_dir)

        if status.status is not ExecutionStatus.SUCCESS:
            return status

        full_output = os.path.join(output_dir, substep.name + RAW_CUT_LABEL + MP4_EXTENSION)

        substep.is_locked = True
        substep.save()
        internal_status = self._internal_raw_cut(screen_full_path, prof_full_path, full_output)
        substep = SubStep.objects.get(pk=substep_id)
        substep.is_locked = False
        substep.save()

        return internal_status

    def raw_cut_async(self, substep_id: int):
        try:
            thread = Thread(target=self.raw_cut, args=[substep_id])
            thread.start()
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut asynchronously: %s', e)

    def _internal_raw_cut(self, video_path1: str, video_path2: str, output_path: str) -> InternalOperationResult:
        status_1 = os.path.isfile(video_path1)
        status_2 = os.path.isfile(video_path2)

        if not status_1 or not status_2:
            self.__logger.warning('Can\'t process invalid videos: %s, %s', video_path1, video_path2)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

        command = settings.FFMPEG_PATH + ' ' + \
                  settings.RAW_CUT_TEMPLATE.format(video_path1, video_path2, output_path)

        status = self._fs_client.execute_command_sync(command)

        if status.status is not ExecutionStatus.SUCCESS:
            return status

    def raw_cut_step(self, step_id: int):
        try:
            substep_ids = SubStep.objects.filter(from_step=step_id).values_list('id', flat=True)
            self._internal_raw_cut_step(substep_ids)
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut_step: %s', e)

    def raw_cut_step_async(self, step_id: int):
        try:
            substep_ids = SubStep.objects.filter(from_step=step_id).values_list('id', flat=True)
            thread = Thread(target=self._internal_raw_cut_step, args=[substep_ids])
            thread.start()
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut_step asynchronously: %s', e)

    def _internal_raw_cut_step(self, substep_ids):
        for ss_id in substep_ids:
            self.raw_cut(ss_id)

    def raw_cut_lesson_async(self, lesson_id: int):
        try:
            step_ids = Step.objects.filter(from_lesson=lesson_id).values_list('id', flat=True)
            thread = Thread(target=self._internal_raw_cut_lesson, args=[step_ids])
            thread.start()
        except Exception as e:
            self.__logger.warning('Can\'t launch raw_cut_lesson asynchronously: %s', e)

    def _internal_raw_cut_lesson(self, step_ids):
        for step_id in step_ids:
            self.raw_cut_step(step_id)

    def _cancel(self):
        if self.__process is not None:
            pid = self.__process.pid
            if self._fs_client.is_process_exists(pid):
                self._fs_client.kill_process(pid)
                self.__process = None
