import os
import os.path
import sys
import signal
import shutil
import time
from stepicstudio.models import Step, UserProfile, Lesson, SubStep, Course
import xml.etree.ElementTree as ET
import xml.parsers.expat
from stepicstudio.utils.extra import translate_non_alphanumerics, deprecated
from STEPIC_STUDIO.settings import ADOBE_LIVE_EXE_PATH
from stepicstudio.const import SUBSTEP_PROFESSOR, FFMPEG_PATH, FFPROBE_RUN_PATH
import subprocess
from distutils.dir_util import copy_tree
import psutil

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


#TODO CHANGE THIS SHIT! ASAP! HATE WINDOWS!
@deprecated
def run_adobe_live() -> None:
    p = [r"D:\stream_profile\stepic_run_camera.bat"]
    global GlobalProcess
    p = [r"C:\Program Files (x86)\Adobe\Flash Media Live Encoder 3.2\FMLECmd.exe",
         "/p", r"C:\StepicServer\static\video\xml_settings.xml"]
    GlobalProcess = subprocess.Popen(p, shell=False)
    print("From Run", GlobalProcess.pid)
    return True

def run_ffmpeg_recorder(path: str, filename: str) -> subprocess.Popen:
    command = FFMPEG_PATH + r' -f dshow -video_size 1920x1080 -rtbufsize 702000k -framerate 25 -i video="Decklink Video ' \
                            r'Capture (3)":audio="Decklink Audio Capture (3)" -threads 0  -preset ultrafast  -c:v libx264 '
    command += path + '\\' + filename
    proc = subprocess.Popen(command, shell=True)
    print("PID = ", proc.pid)
    print(command)
    return proc

#TODO: CHANGE ALL!!!!!!!!!!!!!!!!  stop_path inside is bad, it doesn't support spaces and isn't safe
@deprecated
def stop_adobe_live() -> None:
    p = [r"C:\Program Files (x86)\Adobe\Flash Media Live Encoder 3.2\FMLECmd.exe",
         "/s", r"C:\StepicServer\static\video\xml_settings.xml"]
    tree = ET.parse(r"C:\StepicServer\static\video\xml_settings.xml")
    root = tree.getroot()
    stop_path = None
    for elem in root.iter('path'):
        stop_path = elem.text
        print("stop_adobe_live():", elem.text)
    p = [r"C:\Program Files (x86)\Adobe\Flash Media Live Encoder 3.2\FMLECmd.exe",
         "/s", stop_path]
    subprocess.Popen(p, shell=False)
    if os.path.exists(stop_path):
        print("FILE EXIST!")
    else:
        print(stop_path)
        print("ERROR!!!!!!!!")
        sys.exit(0)


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
        return True


def delete_step_on_disc(**kwargs: dict) -> True | False:
    folder = kwargs["folder_path"]
    data = kwargs["data"]
    f_course = folder + "/" + translate_non_alphanumerics(data["Course"].name)
    f_c_lesson = f_course + "/" + translate_non_alphanumerics(data["Lesson"].name)
    f_c_l_step = f_c_lesson + "/" + translate_non_alphanumerics(data["Step"].name)
    return delete_files_on_server(f_c_l_step)

@deprecated
def files_txt_update(**kwargs):
    pass


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


#TODO: Let's not check if it's fine? Return True anyway?
def delete_files_on_server(path: str) -> True | False:
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    else:
        print(path + ' No folder was found and can\'t be deleted.(This is BAD!)')
        return True

@deprecated
def generate_xml(xml_path: str, write_to_path: str, file_name: str) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for elem in root.iter('path'):
        elem.text = write_to_path.replace("/", "\\") + "\\" + file_name.replace("/", "\\")
    tree.write(xml_path, encoding="UTF-16", short_empty_elements=False)


def rename_element_on_disk(from_obj: 'Step', to_obj: 'Step') -> True or False:
    if os.path.isdir(from_obj.os_path) and not os.path.isdir(to_obj.os_path):
        try:
            os.rename(from_obj.os_path, to_obj.os_path)
            return True
        except Exception as e:
            print(e)
        return False
    else:
        return False

def get_length_in_sec(filename: str) -> int:
    result = subprocess.Popen([FFPROBE_RUN_PATH, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration_string = [x.decode("utf-8") for x in result.stdout.readlines() if "Duration" in x.decode('utf-8')][0]
    time = duration_string.replace(' ', '').split(',')[0].replace('Duration:', '').split(':')
    return int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2].split('.')[0])

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
    summ = 0
    for substep in substep_list:
        for substep_path in substep.os_path_all_variants:
            if os.path.exists(substep_path):
                if not new_step_only:
                    substep.duration = get_length_in_sec(substep_path)
                summ += substep.duration
                substep.save()
                break
    return summ
