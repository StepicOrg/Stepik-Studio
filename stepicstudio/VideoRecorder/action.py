from stepicstudio.models import UserProfile, CameraStatus, Lesson, Step, SubStep, Course
from django.contrib.auth.models import User
from stepicstudio.FileSystemOperations.action import *
from stepicstudio.const import *
from stepicstudio.ssh_connections.screencast import *
from stepicstudio.const import SUBSTEP_PROFESSOR
import time
from stepicstudio.ssh_connections import ScreenRecorder
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus
from STEPIC_STUDIO.settings import LINUX_DIR

import logging

logger = logging.getLogger('stepic_studio.FileSystemOperations.action')

SS_WIN_PATH = ""
SS_LINUX_PATH = ""


def to_linux_translate(win_path: str, username: str) -> str:
    linux_path = LINUX_DIR + username + "/" + '/'.join(win_path.split("/")[1:])
    logger.debug("to_linux_translate() This is linux path %s", linux_path)
    return linux_path


def start_recording(**kwargs: dict) ->InternalOperationResult:
    user_id = kwargs["user_id"]
    username = User.objects.all().get(id=int(user_id)).username
    folder_path = kwargs["user_profile"].serverFilesFolder
    data = kwargs["data"]
    add_file_to_test(folder_path=folder_path, data=data)
    substep_folder, a = substep_server_path(folder_path=folder_path, data=data)

    if 'remote_ubuntu' in kwargs:
        remote_ubuntu = kwargs['remote_ubuntu']
    else:
        remote_ubuntu = None

    # checking SSH connection to linux tab
    screencast_status = ssh_screencast_start(remote_ubuntu)
    if screencast_status.status is not ExecutionStatus.SUCCESS:
        return screencast_status

    # checking ffmpeg execution possibility and start if possible
    # TODO: checking execution possibility without starting ffmpeg
    ffmpeg_status = run_ffmpeg_recorder(substep_folder.replace('/', '\\'), data['currSubStep'].name + SUBSTEP_PROFESSOR)
    if ffmpeg_status.status is not ExecutionStatus.SUCCESS:
        return ffmpeg_status

    try:
        linux_obj = ScreenRecorder(to_linux_translate(substep_folder, username), remote_ubuntu)
        linux_obj.run_screen_recorder(data['currSubStep'].name)
        global SS_LINUX_PATH, SS_WIN_PATH
        SS_LINUX_PATH = linux_obj.remote_path
        SS_WIN_PATH = substep_folder
    except Exception as e:
        stop_ffmpeg_recorder()
        message = "Cannot execute remote ffmpeg: {0}".format(str(e))
        logger.exception("Cannot execute remote ffmpeg")
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message)

    db_camera = CameraStatus.objects.get(id="1")
    if not db_camera.status:
        db_camera.status = True
        db_camera.start_time = int(round(time.time() * 1000))
        db_camera.save()

    return InternalOperationResult(ExecutionStatus.SUCCESS)


def start_subtep_montage(substep_id):
    substep = SubStep.objects.get(id=substep_id)
    video_path_list = substep.os_path_all_variants
    screencast_path_list = substep.os_screencast_path_all_variants
    substep.is_locked = True
    substep.save()
    run_ffmpeg_raw_montage(video_path_list, screencast_path_list, substep_id)



def delete_substep_files(**kwargs):
    folder_path = kwargs["user_profile"].serverFilesFolder
    data = kwargs["data"]
    if data["currSubStep"].is_locked:
        return False
    return delete_substep_on_disc(folder_path=folder_path, data=data)


def delete_step_files(**kwargs):
    folder_path = kwargs["user_profile"].serverFilesFolder
    data = kwargs["data"]
    substeps = SubStep.objects.all().filter(from_step=data['Step'].id)
    for ss in substeps:
        print(ss.name)
        if ss.is_locked:
            return False
    return delete_step_on_disc(folder_path=folder_path, data=data)


# TODO: REMAKE! Wrong implementation
def stop_cam_recording() -> True | False:
    camstat = CameraStatus.objects.get(id="1")
    camstat.status = False
    ssh_screencast_stop()
    camstat.save()

    try:
        stop_ffmpeg_recorder()
    except Exception as e:
        logger.exception("Cannot stop remote ffmpeg screen recorder")

    ssh_obj = ScreenRecorder("_Dummy_")
    ssh_obj.stop_screen_recorder()
    logger.debug("%s %s", SS_LINUX_PATH, SS_WIN_PATH)
    return ssh_obj.get_file(SS_LINUX_PATH, SS_WIN_PATH)


def delete_files_associated(url_args) -> True | False:
    lesson_id = int(url_args[url_args.index(COURSE_ULR_NAME)+3])
    folder_on_server = Lesson.objects.get(id=lesson_id).os_path
    return delete_files_on_server(folder_on_server)
