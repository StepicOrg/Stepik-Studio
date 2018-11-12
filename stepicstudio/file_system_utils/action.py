import logging
import os
import shutil
import subprocess
import time

import psutil

from stepicstudio.const import FFPROBE_RUN_PATH, COURSE_ULR_NAME
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import Step, Lesson, SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections import delete_tablet_lesson_files
from stepicstudio.utils.extra import translate_non_alphanumerics

logger = logging.getLogger('stepic_studio.file_system_utils.action')
MIN_ACCEPTABLE_DIFF = 7.0  # seconds
ATTEMPTS_TO_GET_DURATION = 5
ATTEMPTS_PAUSE = 0.05  # seconds


def delete_substep_on_disc(**kwargs: dict) -> InternalOperationResult:
    data = kwargs['data']

    if data['currSubStep'].is_locked:
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR)

    client = FileSystemClient()
    camera_status = client.remove_file(data['currSubStep'].os_path)
    screencast_status = client.remove_file(data['currSubStep'].os_screencast_path)
    raw_cut_status = client.remove_file(data['currSubStep'].os_automontage_file)

    if camera_status.status is ExecutionStatus.SUCCESS and \
            screencast_status.status is ExecutionStatus.SUCCESS and \
            raw_cut_status.status is ExecutionStatus.SUCCESS:
        return InternalOperationResult(ExecutionStatus.SUCCESS)
    else:
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR)


def delete_server_step_files(**kwargs):
    data = kwargs['data']
    substeps = SubStep.objects.filter(from_step=data['Step'].id)
    for ss in substeps:
        if ss.is_locked:
            return False

    client = FileSystemClient()
    client.delete_recursively(data['Step'].os_automontage_path)
    return client.delete_recursively(data['Step'].os_path).status is ExecutionStatus.SUCCESS


def search_as_files_and_update_info(args: dict) -> dict:
    folder = args['user_profile'].serverFilesFolder
    course = args['Course']
    file_status = [False] * (len(args['all_steps']))
    for index, step in enumerate(args['all_steps']):
        for l in args['all_course_lessons']:
            if step.from_lesson == l.pk and l.from_course == course.pk:
                path = folder + '/' + translate_non_alphanumerics(course.name)
                path += '/' + translate_non_alphanumerics(l.name)
                path += '/' + translate_non_alphanumerics(step.name)
                if os.path.exists(path):
                    file_status[index] = True
                    if not step.is_fresh:
                        step.duration = calculate_folder_duration_in_sec(path)
                        step.is_fresh = True
                        step.save()
                else:
                    pass
    ziped_list = zip(args['all_steps'], file_status)
    ziped_list = list(ziped_list)
    args.update({'all_steps': ziped_list})
    return args


# TODO: Let's not check if it's fine? Return True anyway?
def delete_files_on_server(path: str) -> True | False:
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        return True
    else:
        logger.debug('%s No folder was found and can\'t be deleted.(This is BAD!)', path)
        return True


def rename_element_on_disk(from_obj: 'Step', to_obj: 'Step') -> InternalOperationResult:
    if os.path.exists(to_obj.os_path):
        message = 'File with name \'{0}\' already exists'.format(to_obj.name)
        logger.error(message)
        return InternalOperationResult(ExecutionStatus.FIXABLE_ERROR, message)

    if not os.path.exists(from_obj.os_path):
        #  it may means that step created just now - it's OK
        return InternalOperationResult(ExecutionStatus.SUCCESS)

    if not os.path.isdir(from_obj.os_path):
        message = 'Cannot rename non-existent file: \'{0}\' doesn\'t exist'.format(from_obj.os_path)
        logger.error(message)
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message)

    try:
        os.rename(from_obj.os_path, to_obj.os_path)
    except Exception as e:
        message = 'Cannot rename element on disk: {0}'.format(str(e))
        logger.exception('Cannot rename element on disk')
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message)

    try:
        os.rename(from_obj.os_automontage_path, to_obj.os_automontage_path)
    except Exception as e:
        logger.exception('Cannot rename element on disk: %s', e)

    return InternalOperationResult(ExecutionStatus.SUCCESS)


def get_length_in_sec(filename: str) -> float:
    for _ in range(0, ATTEMPTS_TO_GET_DURATION):
        try:
            result = subprocess.Popen([FFPROBE_RUN_PATH, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            duration_string = [x.decode('utf-8') for x in result.stdout.readlines() if 'Duration' in x.decode('utf-8')][0]
            duration = duration_string.replace(' ', '').split(',')[0].replace('Duration:', '').split(':')
            return float(duration[0]) * 3600 + float(duration[1]) * 60 + float(duration[2])
        except:
            time.sleep(ATTEMPTS_PAUSE)

    logger.warning('Can\'t get duration of substep (%s) for %s sec. File may be in use.',
                   filename,
                   ATTEMPTS_TO_GET_DURATION * ATTEMPTS_PAUSE)
    return 0.0


def calculate_folder_duration_in_sec(calc_path: str, ext: str = 'TS') -> float:
    sec = 0
    if os.path.isdir(calc_path):
        for obj in [o for o in os.listdir(calc_path) if o.endswith(ext) or os.path.isdir('/'.join([calc_path, o]))]:
            sec += calculate_folder_duration_in_sec('/'.join([calc_path, obj]), ext)
        return sec
    else:
        return get_length_in_sec(calc_path)


'''
Function user for updating duration in one substep and in whole stepfolders, returns int with summ seconds
'''


def update_time_records(substep_list, new_step_only=False, new_step_obj=None) -> int:
    summ = 0
    if new_step_only:
        if os.path.exists(new_step_obj.os_path):
            new_step_obj.duration = get_length_in_sec(new_step_obj.os_path)
            new_step_obj.save()
            summ = new_step_obj.duration

        if os.path.exists(new_step_obj.os_screencast_path):
            new_step_obj.screencast_duration = get_length_in_sec(new_step_obj.os_screencast_path)
            new_step_obj.save()

        return summ

    for substep in substep_list:
        if substep.duration \
                and substep.screencast_duration \
                and abs(substep.duration - substep.screencast_duration) < MIN_ACCEPTABLE_DIFF:
            continue

        if os.path.exists(substep.os_path):
            substep.duration = get_length_in_sec(substep.os_path)
            summ += substep.duration

        if os.path.exists(substep.os_screencast_path):
            substep.screencast_duration = get_length_in_sec(substep.os_screencast_path)
        substep.save()

    return summ


def get_free_space(path) -> int:
    try:
        return psutil.disk_usage(path=path).free
    except Exception as e:
        logger.warning('Can\'t get information about disk free space: %s', str(e))
        raise e


def get_storage_capacity(path) -> int:
    try:
        return psutil.disk_usage(path=path).total
    except Exception as e:
        logger.warning('Can\'t get information about total disk capacity: %s', str(e))
        raise e


def get_server_disk_info(path) -> (int, int):
    return get_free_space(path), get_storage_capacity(path)


def delete_files_associated(url_args) -> True | False:
    lesson_id = int(url_args[url_args.index(COURSE_ULR_NAME) + 3])
    lesson = Lesson.objects.get(id=lesson_id)
    folder_on_server = lesson.os_path
    return delete_files_on_server(folder_on_server) and delete_tablet_lesson_files(lesson)
