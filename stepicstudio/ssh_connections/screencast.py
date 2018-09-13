import paramiko
import logging
from stepicstudio.const import PROFESSOR_IP
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD

logger = logging.getLogger('stepic_studio.ssh_connections.screencast')


def ssh_screencast_start(remote_ubuntu):
    if remote_ubuntu is not None:
        global PROFESSOR_IP, UBUNTU_PASSWORD, UBUNTU_USERNAME
        PROFESSOR_IP = remote_ubuntu['professor_ip']
        UBUNTU_USERNAME = remote_ubuntu['ubuntu_username']
        UBUNTU_PASSWORD = remote_ubuntu['ubuntu_password']

    try:
        ssh = paramiko.SSHClient()
        ssh.connect(hostname=PROFESSOR_IP, username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
        ssh.close()
    except Exception as e:
        logger.error("SSH connection to remote linux tab failed: %s", str(e))
        return False

    return True


# TODO: Implement correctly
def ssh_screencast_stop():
    pass