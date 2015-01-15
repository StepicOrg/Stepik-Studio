import paramiko
import time
import os
from stat import S_ISDIR
from STEPIC_STUDIO.settings import UBUNTU_USERNAME, UBUNTU_PASSWORD

#TODO: Class should throw errors.
#TODO: Make it Singleton
class Screen_Recorder(object):

    def __init__(self, path):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect('172.21.202.96', username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
        self.path = path

    def run_screen_recorder(self):
        #stdin, stdout, stderr = ssh.exec_command("uptime")
        command = "ffmpeg -f alsa -ac 2 -i default -f x11grab -r 24 -s 1920x1080 -i :0.0 " \
                  "-pix_fmt yuv420p -vcodec libx264 -preset ultrafast -threads 0 -y " \
                  + self.path + " 2< /dev/null &"
        stdin, stdout, stderr = self.ssh.exec_command(command)

    def stop_screen_recorder(self):
        stdin, stdout, stderr = self.ssh.exec_command("pkill -f ffmpeg")

    def get_file(self, to_path):
        if not self.path:
            raise IOError
        else:
            host = '172.21.202.96'
            transport = paramiko.Transport((host, 22))
            transport.connect(username=UBUNTU_USERNAME, password=UBUNTU_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

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
            download_dir(self.path, to_path)
