import logging

import os
import paramiko

from django.conf import settings


class TabletClient(object):
    def __init__(self):
        self.__logger = logging.getLogger('stepikstudio.ssh_connections.tablet_client')
        self.ssh = None
        self.sftp = None
        self.__connect()

    def __del__(self):
        self.sftp.close()
        self.ssh.close()

    def execute_remote(self, command: str, allowable_code=0, read_output=False) -> str:
        if not self.__is_alive():
            self.__connect()

        _, stdout, _ = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status > 0 and exit_status is not allowable_code:
            self.__logger.error('Can\'t execute %s, exit status: %s', command, exit_status)
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))

        if read_output:
            return stdout.readlines()

    def check_and_create_folder(self, path):
        if not self.__is_alive():
            self.__connect()

        splitted_path = path.split('/')
        splitted_path = list(filter(None, splitted_path))
        temp_path = '/'

        for subfolder in splitted_path:
            temp_path = temp_path + subfolder + '/'
            try:
                self.sftp.stat(temp_path)
            except IOError:
                self.__logger.info('Will create folder %s at tablet', temp_path)
                self.sftp.mkdir(temp_path)

    def download_dir(self, remote_dir, local_dir):
        if not self.__is_alive():
            self.__connect()

        os.path.exists(local_dir) or os.makedirs(local_dir)
        dir_items = self.sftp.listdir_attr(remote_dir)

        for item in dir_items:
            remote_path = remote_dir + '/' + item.filename
            local_path = os.path.join(local_dir, item.filename)


    def __connect(self, attempts=1):
        for _ in range(0, attempts):
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(settings.PROFESSOR_IP,
                             username=settings.UBUNTU_USERNAME,
                             password=settings.UBUNTU_PASSWORD)

            transport = paramiko.Transport((settings.PROFESSOR_IP, 22))
            transport.connect(username=settings.UBUNTU_USERNAME, password=settings.UBUNTU_PASSWORD)
            self.sftp = paramiko.SFTPClient.from_transport(transport)

        if not self.__is_alive():
            raise Exception('Invalid ssh connection')

    def __is_alive(self):
        return self.ssh.get_transport().is_alive()
