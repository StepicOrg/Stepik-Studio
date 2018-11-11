import logging
import os
import re
from stat import S_ISDIR

import paramiko
from django.conf import settings

from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus

logging.getLogger('paramiko').setLevel(logging.WARNING)


class TabletClient(object):
    def __init__(self, connect_timeout=None):
        self.__logger = logging.getLogger('stepikstudio.ssh_connections.tablet_client')
        self.__ssh = None
        self.__sftp = None
        self.__transport = None
        self.timeout = connect_timeout
        try:
            self.__connect()
        except:
            pass

    def __del__(self):
        self.close()

    def execute_remote(self, command: str, allowable_code=0, read_output=False, timeout=None) -> str:
        if not self.__is_alive():
            self.__connect()

        _, stdout, _ = self.__ssh.exec_command(command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status > 0 and exit_status is not allowable_code:
            self.__logger.error('Can\'t execute %s, exit status: %s', command, exit_status)
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))

        if read_output:
            return stdout.readlines()

    def delete_folder(self, path: str) -> (InternalOperationResult, int):
        if not self.__is_alive():
            self.__connect()

        status, size = self.__is_exists(path)
        if status is False:
            return InternalOperationResult(ExecutionStatus.SUCCESS), 0

        try:
            files = self.__sftp.listdir(path=path)
            size = 0

            for f in files:
                size += self.get_file_size(path + '/' + f)
                self.__sftp.remove(path + '/' + f)

            self.__sftp.rmdir(path)
            return InternalOperationResult(ExecutionStatus.SUCCESS), size
        except Exception as e:
            self.__logger.error('Can\'t delete folder %s: %s', path, e)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR), 0

    def delete_folder_recursively(self, path: str):
        if not self.__is_alive():
            self.__connect()

        status, _ = self.__is_exists(path)
        if status is False:
            return InternalOperationResult(ExecutionStatus.SUCCESS)

        files = self.__sftp.listdir(path=path)

        for f in files:
            filepath = path + '/' + f
            try:
                self.__sftp.remove(filepath)
            except IOError:
                self.delete_folder_recursively(filepath)

        self.__sftp.rmdir(path)

    def check_and_create_folder(self, path):
        if not self.__is_alive():
            self.__connect()

        splitted_path = path.split('/')
        splitted_path = list(filter(None, splitted_path))
        temp_path = '/'

        for subfolder in splitted_path:
            temp_path = temp_path + subfolder + '/'
            try:
                self.__sftp.stat(temp_path)
            except IOError:
                self.__sftp.mkdir(temp_path)

    def download_dir(self, remote_dir, local_dir) -> InternalOperationResult:
        try:
            if not self.__is_alive():
                self.__connect()

            os.path.exists(local_dir) or os.makedirs(local_dir)
            dir_items = self.__sftp.listdir_attr(remote_dir)

            for item in dir_items:
                remote_path = remote_dir + '/' + item.filename
                local_path = os.path.join(local_dir, item.filename)
                if S_ISDIR(item.st_mode):
                    status = self.download_dir(remote_path, local_path)
                    if status.status is not ExecutionStatus.SUCCESS:
                        return status
                else:
                    self.__sftp.get(remote_path, local_path)

            return InternalOperationResult(ExecutionStatus.SUCCESS)
        except Exception as e:
            self.__logger.error('Can\'t download remote directory %s: %s', remote_dir, e)
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, e)

    def get_disk_info(self) -> (int, int):
        raw_string_available = self.__get_free_space_info(settings.LINUX_DIR)
        raw_string_total = self.__get_total_space_info(settings.LINUX_DIR)
        free_capacity_bytes = re.findall(r'\d+', raw_string_available[0])
        total_capacity_bytes = re.findall(r'\d+', raw_string_total[0])
        return int(free_capacity_bytes[0]), int(total_capacity_bytes[0])

    def get_file_size(self, path: str) -> int:
        if not self.__is_alive():
            self.__connect()

        info = self.__sftp.stat(path)
        return info.st_size

    def close(self):
        try:
            self.__sftp.close()
            self.__transport.close()
            self.__ssh.close()
        except:
            pass

    def __is_exists(self, path: str) -> (bool, int):
        if not self.__is_alive():
            self.__connect()

        try:
            stat = self.__sftp.stat(path)
            return True, stat.st_size
        except Exception:
            return False, 0

    def __get_free_space_info(self, folder_path) -> str:
        if not self.__is_alive():
            self.__connect()

        command = 'df -B1 ' + folder_path + ' | tail -1 | awk \'{print $4}\''
        return self.execute_remote(command, read_output=True)

    def __get_total_space_info(self, folder_path) -> str:
        if not self.__is_alive():
            self.__connect()

        command = 'df -B1 ' + folder_path + ' | tail -1 | awk \'{print $2}\''
        return self.execute_remote(command, read_output=True)

    def __connect(self, attempts=1):
        try:
            for _ in range(0, attempts):
                self.__ssh = paramiko.SSHClient()
                self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__ssh.connect(settings.PROFESSOR_IP,
                                   username=settings.UBUNTU_USERNAME,
                                   password=settings.UBUNTU_PASSWORD,
                                   timeout=self.timeout)

                self.__transport = paramiko.Transport((settings.PROFESSOR_IP, 22))
                self.__transport.connect(username=settings.UBUNTU_USERNAME,
                                         password=settings.UBUNTU_PASSWORD)
                self.__sftp = paramiko.SFTPClient.from_transport(self.__transport)

        except Exception as e:
            self.__logger.error('SSH connection failed. Reconnecting failed: %s', e)
            raise e

    def __is_alive(self):
        try:
            return self.__ssh.get_transport().is_alive()
        except:
            return False
