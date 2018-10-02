import logging
import paramiko

from django.conf import settings


class TabletClient(object):
    def __init__(self):
        self.__logger = logging.getLogger('stepikstudio.ssh_connections.tablet_client')
        self.__connect()

    def execute_remote(self, command: str) -> str:
        _, stdout, _ = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status > 0:
            raise RuntimeError('Cannot execute command {0} [returned code: {1}]'.format(command, exit_status))
        return stdout.readlines()

    def __connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(settings.PROFESSOR_IP,
                         username=settings.UBUNTU_USERNAME,
                         password=settings.UBUNTU_PASSWORD)

        transport = paramiko.Transport((settings.PROFESSOR_IP, 22))
        transport.connect(username=settings.UBUNTU_USERNAME, password=settings.UBUNTU_PASSWORD)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def __is_alive(self):
        return self.ssh.get_transport().is_alive()
