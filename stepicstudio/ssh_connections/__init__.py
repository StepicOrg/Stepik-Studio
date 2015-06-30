import paramiko
import os
from stat import S_ISDIR
import logging
import time
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD
from stepicstudio.const import SUBSTEP_SCREEN, PROFESSOR_IP

logger = logging.getLogger('stepic_studio.ssh_connections.__init__')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Actually Making it Singleton was bad idea
class ScreenRecorder:

    def __init__(self, path, remote_ubuntu=None):
        self.path = path
        self.remote_path = ''
        self.download_status = False

        if remote_ubuntu is not None:
            global PROFESSOR_IP, UBUNTU_PASSWORD, UBUNTU_USERNAME
            PROFESSOR_IP = remote_ubuntu['professor_ip']
            UBUNTU_USERNAME = remote_ubuntu['ubuntu_username']
            UBUNTU_PASSWORD = remote_ubuntu['ubuntu_password']
            self.path = remote_ubuntu['ubuntu_folder_path'] + "/" + path

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
        self.remote_path = "/"
        logger.debug("I TRY : %s", self.remote_path)
        i = 0
        while i < len(p_args):
            self.remote_path = self.remote_path + p_args[i] + "/"
            if self.rexists(self.remote_path):
                logger.debug("Exist run_screen_recorder() %s", self.remote_path)
            else:
                self.sftp.mkdir(self.remote_path)
                logger.debug("Generated from run_screen_recorder() %s", self.remote_path)
            i += 1

        command = 'ffmpeg -f alsa -ac 2 -i pulse -f x11grab -r 24 -s 1920x1080 -i :0.0 ' \
                  '-pix_fmt yuv420p -vcodec libx264 -acodec pcm_s16le -preset ultrafast -threads 0 -af "volume=1dB" -y ' \
                  + self.remote_path + substepname + SUBSTEP_SCREEN + ' 2< /dev/null &'
        logger.debug(command)
        stdin, stdout, stderr = self.ssh.exec_command(command)

    def stop_screen_recorder(self):
        stdin, stdout, stderr = self.ssh.exec_command("pkill -f ffmpeg")
        time.sleep(2)

    def get_file(self, from_dir, to_path):
        if not self.path:
            raise IOError
        else:
            host = PROFESSOR_IP
            transport = paramiko.Transport((host, 22))
            transport.connect(username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # TODO: Refactor. New connection not needed
            def download_dir(remote_dir, local_dir):
                def _download_status(done_bytes, all_bytes):
                    if done_bytes == all_bytes:
                        logger.debug("Screencast downloaded from: %s", from_dir)
                        print("Screencast downloaded from: %s", from_dir)
                        self.download_status = True
                os.path.exists(local_dir) or os.makedirs(local_dir)
                dir_items = sftp.listdir_attr(remote_dir)
                for item in dir_items:
                    remote_path = remote_dir + '/' + item.filename
                    local_path = os.path.join(local_dir, item.filename)
                    if S_ISDIR(item.st_mode):
                        download_dir(remote_path, local_path)
                    else:
                        global download_status
                        logger.debug('Starting downloading screencast from: %s', from_dir)
                        print('Starting downloading screencast from: %s', from_dir)
                        sftp.get(remote_path, local_path, _download_status)
            download_dir(from_dir, to_path)
            sftp.close()
            return self.download_status

# def get_file_test():
#     global PROFESSOR_IP, UBUNTU_PASSWORD, UBUNTU_USERNAME
#     PROFESSOR_IP = '127.0.0.1'
#     UBUNTU_USERNAME = 'mehanig'
#     UBUNTU_PASSWORD = '123121234151451451451451341234fsdfgafgasdggg'
#     from_path1 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/out1'
#     from_path2 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/out2'
#     from_path3 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/out3'
#     from_path4 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/out4'
#     to_path1 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/in1'
#     to_path2 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/in2'
#     to_path3 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/in3'
#     to_path4 = '/Users/mehanig/CODE/TESTER_FOLDER/__SSH_TESTER/in4'
#
#     sc1 = ScreenRecorder("_dummy_")
#     sc2 = ScreenRecorder("2")
#     sc3 = ScreenRecorder("3")
#     sc4 = ScreenRecorder("4")
#     sc1.get_file(from_path1, to_path1)
#     sc2.get_file(from_path2, to_path2)
#     sc3.get_file(from_path3, to_path3)
#     sc4.get_file(from_path4, to_path4)
#
#
#
# if __name__ == '__main__':
#     get_file_test()
