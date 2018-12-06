import logging
import os

from django.conf import settings

from stepicstudio.file_system_utils.file_system_client import FileSystemClient
from stepicstudio.models import SubStep
from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus

PRPROJ_TEMPLATE = 'template.prproj'
PRPROJ_PRESET = 'ppro.sqpreset'
PRPROJ_SCRIPT = 'create_step_project.jsx'

logger = logging.getLogger(__name__)


class PPROCommandBuilder(object):
    """Appends to PPro command ExtendScript code.
    """

    def __init__(self, base_command):
        self.base_command = base_command + " \""
        self.script_to_include = ''

    def append_opening_document(self, path: str):
        self.base_command += 'app.openDocument(' + '\'' + path + '\'' + ');'
        return self

    # script including should be appended at the end of command
    # use append_eval_file() if you need to execute detached script
    def append_script_including(self, path: str):
        if self.script_to_include:
            raise Exception('Command already contains script including')

        self.script_to_include = ' //@include \'' + path + '\''
        return self

    def append_eval_file(self, path):
        self.base_command += ' $.evalFile(\"' + path + '\");'
        return self

    def append_string_const(self, const_name: str, const_value: str):
        self.base_command += ' const ' + const_name + ' = ' + '\'' + const_value + '\'' + ';'
        return self

    def append_const_array(self, const_name: str, const_values: list):
        values = ''
        for value in const_values:
            values += '\'' + str(value) + '\', '

        self.base_command += ' const ' + const_name + ' = ' + '[' + values + '];'
        return self

    def append_bool_value(self, bool_name: str, bool_value: bool):
        self.base_command += ' boolean ' + bool_name + ' = ' + str(bool_value) + ';'
        return self

    def build(self):
        if self.script_to_include:
            self.base_command += self.script_to_include

        return self.base_command + '\"'


def export_step_to_prproj(step_object) -> InternalOperationResult:
    """Creates PPro project in .prproj format using ExtendScript script.
    Project includes video files of each substep of corresponding step.
    Screencasts and camera recordings puts on different tracks of single sequence.
    :param step_object: step single object.
    """

    screen_files, prof_files = get_target_filenames(step_object.id)
    if not screen_files or not prof_files:
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR,
                                       'Step is empty or substeps are broken.')

    ppro_templates_path = os.path.join(os.path.dirname(__file__), 'adobe_templates')

    try:
        ppro_command = build_ppro_command(step_object.os_path,
                                          ppro_templates_path,
                                          screen_files,
                                          prof_files,
                                          step_object.name)
    except Exception as e:
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, e)

    exec_status = FileSystemClient().execute_command_sync(ppro_command, allowable_code=1)  # may return 1 - it's OK

    if exec_status.status is not ExecutionStatus.SUCCESS:
        logger.error('Cannot execute PPro command: %s \n PPro command: %s', exec_status.message, ppro_command)
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR,
                                       'Cannot execute PPro command. Check PPro configuration.')

    logger.info('Execution of PPro command started; \n PPro command: %s', ppro_command)
    return InternalOperationResult(ExecutionStatus.SUCCESS)


def build_ppro_command(base_path, templates_path, screen_files, prof_files, output_name):
    """Builds Premiere Pro script which should be executed through command line.
    Arguments passes to PPro via declaration ExtendScript variable.
    Command includes base script using #include preprocessor directive
    :param base_path: absolute path to folder which contains target video files;
    :param templates_path: absolute path to .prproj project template and .sqpreset template;
    :param screen_files: list of screencast file names;
    :param prof_files: list of camera recording file names;
    :param output_name: PPro output project name.
    :return PPro command which should be executed using command prompt or shell.
   """

    if not settings.ADOBE_PPRO_PATH:
        raise Exception('Adobe PremierePro configuration is missing. '
                        'Please, specify path to PremierePro in config file.')

    base_command = settings.ADOBE_PPRO_PATH + ' ' + settings.ADOBE_PPRO_CMD
    prproj_template_path = os.path.join(templates_path, PRPROJ_TEMPLATE)
    prproj_preset_path = os.path.join(templates_path, PRPROJ_PRESET)
    script_path = os.path.join(os.path.dirname(__file__), 'adobe_scripts', PRPROJ_SCRIPT)

    if not os.path.isfile(prproj_template_path):
        raise Exception('Template of PremierPro project is missing. '
                        'Please, create empty PPro project at {}'.format(prproj_template_path))

    if not os.path.isfile(prproj_preset_path):
        raise Exception('.sqpreset sequence template file is missing. '
                        'Please, put .sqpreset at {}'.format(prproj_preset_path))

    return PPROCommandBuilder(base_command) \
        .append_opening_document(prproj_template_path.replace(os.sep, '\\\\')) \
        .append_string_const('outputName', output_name) \
        .append_string_const('basePath', base_path.replace(os.sep, '\\\\')) \
        .append_string_const('presetPath', prproj_preset_path.replace(os.sep, '\\\\')) \
        .append_const_array('screenVideos', screen_files) \
        .append_const_array('professorVideos', prof_files) \
        .append_script_including(script_path.replace(os.sep, '\\\\')) \
        .build()


def get_target_filenames(step_id):
    screen_files = []
    prof_files = []

    for substep in SubStep.objects.filter(from_step=step_id).order_by('start_time'):
        if substep.is_videos_ok and \
                os.path.isfile(substep.os_screencast_path) and \
                os.path.isfile(substep.os_path):
            screen_files.append(substep.screencast_name)
            prof_files.append(substep.camera_recording_name)

    return screen_files, prof_files
