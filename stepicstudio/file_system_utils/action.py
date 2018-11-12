import logging
import os
import shutil
import subprocess
import time

import psutil

from stepicstudio.const import FFPROBE_RUN_PATH, COURSE_ULR_NAME
from stepicstudio.models import Step, Lesson
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections import delete_tablet_lesson_files
from stepicstudio.utils.extra import translate_non_alphanumerics

logger = logging.getLogger('stepic_studio.file_system_utils.action')
MIN_ACCEPTABLE_DIFF = 7.0  # seconds
ATTEMPTS_TO_GET_DURATION = 5
ATTEMPTS_PAUSE = 0.05  # seconds


def substep_server_path(**kwargs: dict) -> (str, str):
    folder = kwargs['folder_path']
    data = kwargs['data']
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f_course = folder + '/' + translate_non_alphanumerics(data['Course'].name)
    if not os.path.isdir(f_course):
        os.makedirs(f_course)

    f_c_lesson = f_course + '/' + translate_non_alphanumerics(data['Lesson'].name)

    if not os.path.isdir(f_c_lesson):
        os.makedirs(f_c_lesson)

    f_c_l_step = f_c_lesson + '/' + translate_non_alphanumerics(data['Step'].name)
    if not os.path.isdir(f_c_l_step):
        os.makedirs(f_c_l_step)

    f_c_l_s_substep = f_c_l_step + '/' + translate_non_alphanumerics(data['currSubStep'].name)
    return f_c_l_s_substep, f_c_l_step


def add_file_to_test(**kwargs: dict) -> None:
    folder_p, a = substep_server_path(**kwargs)
    if not os.path.isdir(folder_p):
        os.makedirs(folder_p)


def delete_substep_on_disc(**kwargs: dict) -> InternalOperationResult:
    folder = kwargs['folder_path']
    data = kwargs['data']
    f_course = os.path.join(folder, translate_non_alphanumerics(data['Course'].name))
    f_c_lesson = os.path.join(f_course, translate_non_alphanumerics(data['Lesson'].name))
    f_c_l_step = os.path.join(f_c_lesson, translate_non_alphanumerics(data['Step'].name))
    f_c_l_s_substep = os.path.join(f_c_l_step, translate_non_alphanumerics(data['currSubStep'].name))

    delete_files_on_server(data['currSubStep'].os_automontage_path)

    if not os.path.exists(f_c_l_s_substep):
        return InternalOperationResult(ExecutionStatus.SUCCESS)

    if not os.path.isdir(f_c_l_s_substep):
        logger.warning('Server file removing failed: %s is not directory', f_c_l_s_substep)
        return InternalOperationResult(ExecutionStatus.FIXABLE_ERROR,
                                       '{} is not directory'.format(f_c_l_s_substep))
    else:
        try:
            shutil.rmtree(f_c_l_s_substep)
        except Exception as e:
            logger.warning('Server file removing failed: %s', e)
            return InternalOperationResult(ExecutionStatus.FIXABLE_ERROR,
                                           'Error while deleting substep. Files may be in use by other application.')
        if os.path.exists(f_c_l_s_substep):
            time.sleep(0.75)
        return InternalOperationResult(ExecutionStatus.SUCCESS)


def delete_step_on_disc(**kwargs: dict) -> True | False:
    folder = kwargs['folder_path']
    data = kwargs['data']
    f_course = folder + '/' + translate_non_alphanumerics(data['Course'].name)
    f_c_lesson = f_course + '/' + translate_non_alphanumerics(data['Lesson'].name)
    f_c_l_step = f_c_lesson + '/' + translate_non_alphanumerics(data['Step'].name)
    delete_files_on_server(data['Step'].os_automontage_path)
    return delete_files_on_server(f_c_l_step)


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

    logger.warning('Can\'t get duration of substep (%s) for %s sec. File may be in use.', filename, ATTEMPTS_TO_GET_DURATION * ATTEMPTS_PAUSE)
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
    if new_step_only:
        for substep_path in new_step_obj.os_path_all_variants:
            if os.path.exists(substep_path):
                new_step_obj.duration = get_length_in_sec(substep_path)
                new_step_obj.save()
        for substep_scr_path in new_step_obj.os_screencast_path_all_variants:
            if os.path.exists(substep_scr_path):
                new_step_obj.screencast_duration = get_length_in_sec(substep_scr_path)
                new_step_obj.save()
    summ = 0
    for substep in substep_list:
        if substep.duration \
                and substep.screencast_duration \
                and abs(substep.duration - substep.screencast_duration) < MIN_ACCEPTABLE_DIFF:
            continue
        for substep_path in substep.os_path_all_variants:
            if os.path.exists(substep_path):
                if not new_step_only:
                    substep.duration = get_length_in_sec(substep_path)
                summ += substep.duration
                break
        for substep_scr_path in substep.os_screencast_path_all_variants:
            if os.path.exists(substep_scr_path):
                if not new_step_only:
                    substep.screencast_duration = get_length_in_sec(substep_scr_path)
                break
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
