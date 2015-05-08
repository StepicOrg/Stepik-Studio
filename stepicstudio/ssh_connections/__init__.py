import paramiko
import os
from stat import S_ISDIR
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD
from stepicstudio.const import SUBSTEP_SCREEN, PROFESSOR_IP

#TODO: Class should throw errors.
#TODO: Make it Singleton
class Screen_Recorder(object):

    def __init__(self, path):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(PROFESSOR_IP, username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
        self.path = path
        self.remote_path = ''

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

    def run_screen_recorder(self):
        #stdin, stdout, stderr = ssh.exec_command("uptime")
        p_args = self.path.split('/')
        p_args = list(filter(None, p_args))
        self.remote_path = "/"
        print("I TRY : ", self.remote_path)
        i = 0
        while i < len(p_args):
            self.remote_path = self.remote_path + p_args[i] + "/"
            if self.rexists(self.remote_path):
                print("Exist run_screen_recorder()", self.remote_path)
            else:
                self.sftp.mkdir(self.remote_path)
                print("Generated from run_screen_recorder()", self.remote_path)
            i += 1

        command = 'ffmpeg -f alsa -ac 2 -i pulse -f x11grab -r 24 -s 1920x1080 -i :0.0 ' \
                  '-pix_fmt yuv420p -vcodec libx264 -acodec pcm_s16le -preset ultrafast -threads 0 -af "volume=1dB" -y ' \
                  + self.remote_path + SUBSTEP_SCREEN + ' 2< /dev/null &'
        print(command)
        stdin, stdout, stderr = self.ssh.exec_command(command)


    def stop_screen_recorder(self):
        stdin, stdout, stderr = self.ssh.exec_command("pkill -f ffmpeg")

    def get_file(self, from_dir, to_path):
        if not self.path:
            raise IOError
        else:
            host = PROFESSOR_IP
            transport = paramiko.Transport((host, 22))
            transport.connect(username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            #TODO: Refactor. New connection not needed
            def download_dir(remote_dir, local_dir):
                os.path.exists(local_dir) or os.makedirs(local_dir)
                dir_items = sftp.listdir_attr(remote_dir)
                for item in dir_items:
                    remote_path = remote_dir + '/' + item.filename
                    local_path = os.path.join(local_dir, item.filename)
                    if S_ISDIR(item.st_mode):
                        download_dir(remote_path, local_path)
                    else:
                        sftp.get(remote_path, local_path)
            download_dir(from_dir, to_path)
            sftp.close()