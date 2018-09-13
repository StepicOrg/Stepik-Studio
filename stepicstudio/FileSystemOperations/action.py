import os
import shutil
from stepicstudio.models import Step, UserProfile, Lesson, SubStep, Course
from stepicstudio.utils.extra import translate_non_alphanumerics
from stepicstudio.const import FFPROBE_RUN_PATH, FFMPEGcommand, FFMPEG_PATH
import subprocess
import psutil
from stepicstudio.state import CURRENT_TASKS_DICT

import logging

logger = logging.getLogger('stepic_studio.FileSystemOperations.action')

GlobalProcess = None


def substep_server_path(**kwargs: dict) -> (str, str):
    folder = kwargs["folder_path"]
    data = kwargs["data"]
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f_course = folder + "/" + translate_non_alphanumerics(data["Course"].name)
    if not os.path.isdir(f_course):
        os.makedirs(f_course)

    f_c_lesson = f_course + "/" + translate_non_alphanumerics(data["Lesson"].name)

    if not os.path.isdir(f_c_lesson):
        os.makedirs(f_c_lesson)

    f_c_l_step = f_c_lesson + "/" + translate_non_alphanumerics(data["Step"].name)
    if not os.path.isdir(f_c_l_step):
        os.makedirs(f_c_l_step)

    f_c_l_s_substep = f_c_l_step + "/" + translate_non_alphanumerics(data["currSubStep"].name)
    return f_c_l_s_substep, f_c_l_step


def add_file_to_test(**kwargs: dict) -> None:
    folder_p, a = substep_server_path(**kwargs)
    if not os.path.isdir(folder_p):
        os.makedirs(folder_p)

    return True


def run_ffmpeg_recorder(path: str, filename: str) -> True | False:
    command = FFMPEGcommand
    command += path + '\\' + filename

    try:
        global process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # process still running when returncode is None
        if process.returncode is not None or process.returncode != 0:
            _, error = process.communicate()
            logger.error("Cannot exec ffmpeg command (%s): %s", process.returncode, error)
            return False
    except Exception as e:
        logger.error("Cannot exec ffmpeg command: %s", str(e))
        return False

    logger.info('Successful starting ffmpeg (PID: %s; FFMPEG command: %s)', process.pid, command)
    return True


def run_ffmpeg_raw_montage(video_path_list: list, screencast_path_list: list, substep_id):
    try:
        video_path = [i for i in video_path_list if os.path.exists(i)][0]
        screencast_path = [i for i in screencast_path_list if os.path.exists(i)][0]
        to_folder_path = os.path.dirname(screencast_path)
        filename_to_create = os.path.basename(os.path.dirname(screencast_path))+'_Raw_Montage.mp4'
        command = FFMPEG_PATH + r' -i ' + video_path + r' -i ' + screencast_path + r' -filter_complex \
        "[0:v]setpts=PTS-STARTPTS, pad=iw*2:ih[bg]; \
        [1:v]setpts=PTS-STARTPTS[fg]; [bg][fg]overlay=w; \
        amerge,pan=stereo:c0<c0+c1:c1<c1+c0" ' + to_folder_path + "/" + filename_to_create + " -y"
        proc = subprocess.Popen(command, shell=True)
        CURRENT_TASKS_DICT.update({proc: substep_id})

    except Exception as e:
        logger.debug('run_ffmepg_raw_mongage: Error')


# TODO: problems with stopping ffmpeg process
def stop_ffmpeg_recorder(proc: subprocess.Popen) -> None:
    def kill_proc_tree(pid, including_parent=True):
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        if including_parent:
            parent.kill()

    kill_proc_tree(proc.pid)


def delete_substep_on_disc(**kwargs: dict) -> True | False:
    folder = kwargs["folder_path"]
    data = kwargs["data"]
    f_course = folder + "/" + translate_non_alphanumerics(data["Course"].name)
    f_c_lesson = f_course + "/" + translate_non_alphanumerics(data["Lesson"].name)
    f_c_l_step = f_c_lesson + "/" + translate_non_alphanumerics(data["Step"].name)
    f_c_l_s_substep = f_c_l_step + "/" + translate_non_alphanumerics(data["currSubStep"].name)
    if not os.path.isdir(f_c_l_s_substep):
        return False
    else:
        shutil.rmtree(f_c_l_s_substep)
        while os.path.exists(f_c_l_s_substep):
            pass
        return True


def delete_step_on_disc(**kwargs: dict) -> True | False:
    folder = kwargs["folder_path"]
    data = kwargs["data"]
    f_course = folder + "/" + translate_non_alphanumerics(data["Course"].name)
    f_c_lesson = f_course + "/" + translate_non_alphanumerics(data["Lesson"].name)
    f_c_l_step = f_c_lesson + "/" + translate_non_alphanumerics(data["Step"].name)
    return delete_files_on_server(f_c_l_step)


def search_as_files_and_update_info(args: dict) -> dict:
    folder = args["user_profile"].serverFilesFolder
    course = args["Course"]
    file_status = [False] * (len(args["all_steps"]))
    for index, step in enumerate(args["all_steps"]):
        for l in args["all_course_lessons"]:
            if step.from_lesson == l.pk and l.from_course == course.pk:
                path = folder + "/" + translate_non_alphanumerics(course.name)
                path += "/" + translate_non_alphanumerics(l.name)
                path += "/" + translate_non_alphanumerics(step.name)
                if os.path.exists(path):
                    file_status[index] = True
                    if not step.is_fresh:
                        step.duration = calculate_folder_duration_in_sec(path)
                        step.is_fresh = True
                        step.save()
                else:
                    pass
    ziped_list = zip(args["all_steps"], file_status)
    ziped_list = list(ziped_list)
    args.update({"all_steps": ziped_list})
    return args


# TODO: Let's not check if it's fine? Return True anyway?
def delete_files_on_server(path: str) -> True | False:
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    else:
        logger.debug('%s No folder was found and can\'t be deleted.(This is BAD!)', path)
        return True


def rename_element_on_disk(from_obj: 'Step', to_obj: 'Step') -> True or False:
    if os.path.isdir(from_obj.os_path) and not os.path.isdir(to_obj.os_path):
        try:
            os.rename(from_obj.os_path, to_obj.os_path)
            return True
        except Exception as e:
            logger.error('Cannot rename element on disk: %s', str(e))
            return False
    else:
        if not os.path.isdir(from_obj.os_path):
            logger.error("Cannot rename non-existent file: %s doesn't exist", from_obj.os_path)

        if os.path.isdir(to_obj.os_path):
            logger.error("File with name '%s' already exists", to_obj.name)

        return False


def get_length_in_sec(filename: str) -> int:
    try:
        result = subprocess.Popen([FFPROBE_RUN_PATH, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        duration_string = [x.decode("utf-8") for x in result.stdout.readlines() if "Duration" in x.decode('utf-8')][0]
        time = duration_string.replace(' ', '').split(',')[0].replace('Duration:', '').split(':')
        result = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2].split('.')[0])
    except Exception as e:
        return 0
    return result


def calculate_folder_duration_in_sec(calc_path: str, ext: str='TS') -> int:
    sec = 0
    if os.path.isdir(calc_path):
        for obj in [o for o in os.listdir(calc_path) if o.endswith(ext) or os.path.isdir('/'.join([calc_path, o]))]:
            sec += calculate_folder_duration_in_sec('/'.join([calc_path, obj]), ext)
        return sec
    else:
        return get_length_in_sec(calc_path)

"""
Function user for updating duration in one substep and in whole stepfolders, returns int with summ seconds
"""
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
