from django.conf import settings

from stepicstudio.const import SUBSTEP_PROFESSOR, SUBSTEP_SCREEN, MP4_EXTENSION
from stepicstudio.file_system_utils.action import *
from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import CameraStatus
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.postprocessing import synchronize_videos
from stepicstudio.scheduling.task_manager import TaskManager
from stepicstudio.video_recorders.camera_recorder import ServerCameraRecorder
from stepicstudio.video_recorders.tablet_recorder import TabletScreenRecorder

logger = logging.getLogger(__name__)


def start_recording(substep) -> InternalOperationResult:
    create_status = FileSystemClient().create_recursively(substep.dir_path)

    if create_status.status is not ExecutionStatus.SUCCESS:
        logger.error('Can\'t create folder for new substep: %s', create_status.message)
        return create_status

    tablet_exec_info = TabletScreenRecorder().start_recording(substep.os_tablet_dir, substep.name + SUBSTEP_SCREEN)

    if tablet_exec_info.status is not ExecutionStatus.SUCCESS:
        return tablet_exec_info

    ffmpeg_status = ServerCameraRecorder().start_recording(substep.dir_path, substep.name + SUBSTEP_PROFESSOR)

    if ffmpeg_status.status is not ExecutionStatus.SUCCESS:
        TabletScreenRecorder().stop_recording()
        return ffmpeg_status

    db_camera = CameraStatus.objects.get(id='1')
    if not db_camera.status:
        db_camera.status = True
        db_camera.start_time = int(round(time.time() * 1000))
        db_camera.save()

    return InternalOperationResult(ExecutionStatus.SUCCESS)


def stop_cam_recording() -> True | False:
    camstat = CameraStatus.objects.get(id='1')
    camstat.status = False
    camstat.save()

    stop_screen_status = TabletScreenRecorder().stop_recording()
    stop_camera_status = ServerCameraRecorder().stop_recording()

    # if stop status is FIXABLE_ERROR - let's try to download file anyway
    if stop_camera_status.status is ExecutionStatus.FATAL_ERROR or \
            stop_screen_status.status is ExecutionStatus.FATAL_ERROR:
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
