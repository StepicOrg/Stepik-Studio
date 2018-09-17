import paramiko
import logging
from stepicstudio.const import PROFESSOR_IP
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD
from stepicstudio.operationsstatuses.operation_result import InternalOperationResult
from stepicstudio.operationsstatuses.statuses import ExecutionStatus

logger = logging.getLogger('stepic_studio.ssh_connections.screencast')


def ssh_screencast_start(remote_ubuntu=None) -> InternalOperationResult:
    if remote_ubuntu is not None:
        global PROFESSOR_IP, UBUNTU_PASSWORD, UBUNTU_USERNAME
        PROFESSOR_IP = remote_ubuntu['professor_ip']
        UBUNTU_USERNAME = remote_ubuntu['ubuntu_username']
        UBUNTU_PASSWORD = remote_ubuntu['ubuntu_password']

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=PROFESSOR_IP, username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
        ssh.close()
    except Exception as e:
        message = "SSH connection to remote linux tab failed: {0}".format(str(e))
        logger.exception("SSH connection to remote linux tab failed:")
        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, message)

    return InternalOperationResult(ExecutionStatus.SUCCESS)


# TODO: Implement correctly
def ssh_screencast_stop():
    pass
