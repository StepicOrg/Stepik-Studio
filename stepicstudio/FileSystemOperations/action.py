import os
import os.path
import sys
import signal
import shutil
import time
import xml.etree.ElementTree as ET
import xml.parsers.expat
from stepicstudio.utils.extra import translate_non_alphanumerics, deprecated
from STEPIC_STUDIO.settings import ADOBE_LIVE_EXE_PATH
from stepicstudio.const import SUBSTEP_PROFESSOR, FFMPEG_PATH
import subprocess
from distutils.dir_util import copy_tree
import psutil

GlobalProcess = None

def substep_server_path(**kwargs):
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


def add_file_to_test(**kwargs):
    folder_p, a = substep_server_path(**kwargs)
    if not os.path.isdir(folder_p):
        os.makedirs(folder_p)

    return True


#TODO CHANGE THIS SHIT! ASAP! HATE WINDOWS!
@deprecated
def run_adobe_live():
    p = [r"D:\stream_profile\stepic_run_camera.bat"]
    global GlobalProcess
    p = [r"C:\Program Files (x86)\Adobe\Flash Media Live Encoder 3.2\FMLECmd.exe",
         "/p", r"C:\StepicServer\static\video\xml_settings.xml"]
    GlobalProcess = subprocess.Popen(p, shell=False)
    print("From Run", GlobalProcess.pid)
    return True

def run_ffmpeg_recorder(path, filename):
    command = FFMPEG_PATH + r' -f dshow -video_size 1920x1080 -rtbufsize 702000k -framerate 25 -i video="Decklink Video ' \
                            r'Capture (3)":audio="Decklink Audio Capture (3)" -threads 0  -preset ultrafast  -c:v libx264 '
    command += path + '\\' + filename
    proc = subprocess.Popen(command, shell=True)
    print("PID = ", proc.pid)
    print(command)
    return proc

#TODO: CHANGE ALL!!!!!!!!!!!!!!!!  stop_path inside is bad, it doesn't support spaces and isn't safe
@deprecated
def stop_adobe_live():
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


def stop_ffmpeg_recorder(proc: "Process"):
    def kill_proc_tree(pid, including_parent=True):
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        if including_parent:
            parent.kill()

    kill_proc_tree(proc.pid)


def delete_substep_on_disc(**kwargs: dict) -> True or False:
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


def delete_step_on_disc(**kwargs: dict):
    folder = kwargs["folder_path"]
    data = kwargs["data"]
    f_course = folder + "/" + translate_non_alphanumerics(data["Course"].name)
    f_c_lesson = f_course + "/" + translate_non_alphanumerics(data["Lesson"].name)
    f_c_l_step = f_c_lesson + "/" + translate_non_alphanumerics(data["Step"].name)
    return delete_files_on_server(f_c_l_step)

@deprecated
def files_txt_update(**kwargs):
    pass


def search_as_files(args):
    folder = args["user_profile"].serverFilesFolder
    course = args["Course"]
    file_status = [False] * (len(args["all_steps"]))
    for index, step in enumerate(args["all_steps"]):
        for l in args["all_course_lessons"]:
            if step.from_lesson == l.pk and l.from_course == course.pk:
                print(step.name)
                path = folder + "/" + translate_non_alphanumerics(course.name)
                path += "/" + translate_non_alphanumerics(l.name)
                path += "/" + translate_non_alphanumerics(step.name)
                if os.path.exists(path):
                    # print(path + " EXIST")
                    file_status[index] = True
                else:
                    # print("NO FILE")
                    pass
    ziped_list = zip(args["all_steps"], file_status)
    ziped_list = list(ziped_list)
    args.update({"all_steps": ziped_list})
    return args


#TODO: Let's not check if it's fine? Return True anyway?
def delete_files_on_server(path: str) -> True:
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    else:
        print(path + ' No folder was found and can\'t be deleted.(This is BAD!)')
        return True

@deprecated
def generate_xml(XMLpath, write_to_path, file_name):
    tree = ET.parse(XMLpath)
    root = tree.getroot()
    for elem in root.iter('path'):
        elem.text = write_to_path.replace("/", "\\") + "\\" + file_name.replace("/", "\\")
    #     # <?xml version="1.0" encoding="UTF-16"?>
    tree.write(XMLpath, encoding="UTF-16", short_empty_elements=False)
    # ElementTree.tostring(tree, encoding='utf-16')


def rename_element_on_disk(FromObj, ToObj):
    if os.path.isdir(FromObj.os_path) and not os.path.isdir(ToObj.os_path):
        try:
            ignore_func = shutil.ignore_patterns('.DS_Store', )
            os.rename(FromObj.os_path, ToObj.os_path)
            return True
        except Exception as e:
            print(e)
        return False
    else:
        return False