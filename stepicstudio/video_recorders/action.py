from django.contrib.auth.models import User

from stepicstudio import const
from stepicstudio.const import *
from stepicstudio.const import SUBSTEP_PROFESSOR
from stepicstudio.file_system_utils.action import *
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import CameraStatus, SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.postprocessing import synchronize_videos
from stepicstudio.scheduling.task_manager import TaskManager
from stepicstudio.video_recorders.camera_recorder import ServerCameraRecorder
from stepicstudio.video_recorders.tablet_recorder import TabletScreenRecorder

logger = logging.getLogger('stepic_studio.file_system_utils.action')


def to_linux_translate(win_path: str, username: str) -> str:
    linux_path = settings.LINUX_DIR + username + '/' + '/'.join(win_path.split('/')[1:])
    logger.debug('to_linux_translate() This is linux path %s', linux_path)
    return linux_path


def start_recording(**kwargs: dict) -> InternalOperationResult:
    user_id = kwargs['user_id']
    username = User.objects.get(id=int(user_id)).username
    folder_path = kwargs['user_profile'].serverFilesFolder
    data = kwargs['data']
    add_file_to_test(folder_path=folder_path, data=data)
    substep_folder, a = substep_server_path(folder_path=folder_path, data=data)

    filename = data['currSubStep'].name + const.SUBSTEP_SCREEN
    folder = to_linux_translate(substep_folder, username)

    try:
        remote_status = TabletScreenRecorder().start_recording(folder, filename)
    except:
        remote_status = InternalOperationResult(ExecutionStatus.FATAL_ERROR)

    if remote_status.status is not ExecutionStatus.SUCCESS:
        return remote_status

    ffmpeg_status = ServerCameraRecorder().start_recording(substep_folder.replace('/', '\\'),
                                                           data['currSubStep'].name + SUBSTEP_PROFESSOR)

    if ffmpeg_status.status is not ExecutionStatus.SUCCESS:
        TabletScreenRecorder().stop_recording()
        return ffmpeg_status

    db_camera = CameraStatus.objects.get(id='1')
    if not db_camera.status:
        db_camera.status = True
        db_camera.start_time = int(round(time.time() * 1000))
        db_camera.save()

    return InternalOperationResult(ExecutionStatus.SUCCESS)


def delete_server_substep_files(**kwargs):
    folder_path = kwargs['user_profile'].serverFilesFolder
    data = kwargs['data']
    if data['currSubStep'].is_locked:
        return InternalOperationResult(ExecutionStatus.FIXABLE_ERROR,
                                       'File is locked. Please wait for unlocking.')

    return delete_substep_on_disc(folder_path=folder_path, data=data)


def delete_server_step_files(**kwargs):
    folder_path = kwargs['user_profile'].serverFilesFolder
    data = kwargs['data']
    substeps = SubStep.objects.filter(from_step=data['Step'].id)
    for ss in substeps:
        if ss.is_locked:
            return False
    return delete_step_on_disc(folder_path=folder_path, data=data)


def stop_cam_recording() -> True | False:
    camstat = CameraStatus.objects.get(id='1')
    camstat.status = False
    camstat.save()

    stop_screen_status = TabletScreenRecorder().stop_recording()
    stop_camera_status = ServerCameraRecorder().stop_recording()

    if stop_camera_status.status is not ExecutionStatus.SUCCESS or \
                    stop_screen_status.status is not ExecutionStatus.SUCCESS:
        return False

    TabletScreenRecorder().download_last_recording(ServerCameraRecorder().last_processed_path)

    professor_video = os.path.join(ServerCameraRecorder().last_processed_path,
                                   ServerCameraRecorder().last_processed_file)

    screen_video = os.path.join(ServerCameraRecorder().last_processed_path,
                                TabletScreenRecorder().last_processed_file)

    if settings.REENCODE_TABLET:
        convert_mkv_to_mp4(ServerCameraRecorder().last_processed_path,
                           TabletScreenRecorder().last_processed_file)

    TaskManager().run_once_time(synchronize_videos, args=[professor_video, screen_video])

    return True


def convert_mkv_to_mp4(path: str, filename: str):
    new_filename = os.path.splitext(filename)[0] + MP4_EXTENSION  # change file extension from .mkv to .mp4
    source_file = os.path.join(path, filename)
    target_file = os.path.join(path, new_filename)
    fs_client = FileSystemClient()

    if not os.path.isfile(source_file):
        logger.error('Converting mkv to mp4 failed; file %s doesn\'t exist', source_file)
        return

    reencode_command = settings.FFMPEG_PATH + ' ' + \
                       settings.TABLET_REENCODE_TEMPLATE.format(source_file, target_file)

    result, _ = fs_client.execute_command(reencode_command)

    if result.status is ExecutionStatus.SUCCESS:
        logger.info('Successfully start converting mkv to mp4 (FFMPEG command: %s)', reencode_command)
    else:
        logger.error('Converting mkv to mp4 failed: %s; FFMPEG command: %s', result.message, reencode_command)

