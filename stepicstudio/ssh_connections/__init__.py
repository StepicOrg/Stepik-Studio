import paramiko
import os
from stat import S_ISDIR
import logging
import time
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD
from stepicstudio.const import SUBSTEP_SCREEN, PROFESSOR_IP
from django.conf import settings

logger = logging.getLogger('stepic_studio.ssh_connections.__init__')
logging.getLogger('paramiko').setLevel(logging.WARNING)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Actually Making it Singleton was bad idea
class TabletClient(object):
    def __init__(self, path, remote_ubuntu=None):
        self.path = path
        self.remote_path = ''
        self.download_status = False

        if remote_ubuntu is not None:
            global PROFESSOR_IP, UBUNTU_PASSWORD, UBUNTU_USERNAME
            PROFESSOR_IP = remote_ubuntu['professor_ip']
            UBUNTU_USERNAME = remote_ubuntu['ubuntu_username']
            UBUNTU_PASSWORD = remote_ubuntu['ubuntu_password']
            self.path = remote_ubuntu['ubuntu_folder_path'] + '/' + path

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(PROFESSOR_IP, username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)

        host = PROFESSOR_IP
        transport = paramiko.Transport((host, 22))
        transport.connect(username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def rexists(self, path):
        try:
            self.sftp.stat(path)
        except IOError:
            return False
        else:
            return True

    def run_screen_recorder(self, substepname=''):
        p_args = self.path.split('/')
        p_args = list(filter(None, p_args))
        self.remote_path = '/'
        logger.debug('I TRY : %s', self.remote_path)
        i = 0
        while i < len(p_args):
            self.remote_path = self.remote_path + p_args[i] + '/'
            if self.rexists(self.remote_path):
                logger.debug('Exist run_screen_recorder() %s', self.remote_path)
            else:
                self.sftp.mkdir(self.remote_path)
                logger.debug('Generated from run_screen_recorder() %s', self.remote_path)
            i += 1

        command = settings.FFMPEG_TABLET_CMD + self.remote_path + substepname + SUBSTEP_SCREEN + ' 2< /dev/null &'
        logger.debug(command)
        stdin, stdout, stderr = self.ssh.exec_command(command)

    def stop_screen_recorder(self):
        command = 'pkill -f ffmpeg'
        _, stdout, _ = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status > 0:
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))

    def get_file(self, from_dir, to_path):
        if not self.path:
            raise IOError
        try:
            host = PROFESSOR_IP
            transport = paramiko.Transport((host, 22))
            transport.connect(username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            logger.exception('Finaly catched SSH Error! GOTCHA!')
            raise e

        # TODO: Refactor. New connection not needed
        def download_dir(remote_dir, local_dir):
            def _download_status(done_bytes, all_bytes):
                if done_bytes == all_bytes:
                    logger.debug('Screencast downloaded from: %s', from_dir)
                    print('Screencast downloaded from: %s', from_dir)
                    self.download_status = True

            os.path.exists(local_dir) or os.makedirs(local_dir)
            dir_items = sftp.listdir_attr(remote_dir)
            filename = None
            for item in dir_items:
                filename = item.filename
                remote_path = remote_dir + '/' + item.filename
                local_path = os.path.join(local_dir, item.filename)
                if S_ISDIR(item.st_mode):
                    download_dir(remote_path, local_path)
                else:
                    global download_status
                    logger.debug('Starting downloading screencast from: %s', from_dir)
                    print('Starting downloading screencast from: %s', from_dir)
                    sftp.get(remote_path, local_path, _download_status)

            return filename

        downloaded_filename = download_dir(from_dir, to_path)
        sftp.close()
        return self.download_status, downloaded_filename

    def get_free_space_info(self, folder_path) -> str:
        command = 'df -B1 ' + folder_path + ' | tail -1 | awk \'{print $4}\''
        _, stdout, _ = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status > 0:
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))
        return stdout.readlines()

    def get_total_space_info(self, folder_path) -> str:
        command = 'df -B1 ' + folder_path + ' | tail -1 | awk \'{print $2}\''
        _, stdout, _ = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status > 0:
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))
        return stdout.readlines()
