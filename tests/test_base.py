import stepicstudio.VideoRecorder.action as VR
from . import Helper

class TestDBandAuth(object):

    def test_db_reachable(self):
        from django.db import connections

        conn = connections['default']
        try:
            conn.cursor()
        except OperationalError:
            reachable = False
        else:
            reachable = True

        assert reachable

    def test_auth_system_for_tester(self):
        from django.contrib import auth
        user = auth.authenticate(username='tester', password='tester')
        assert user is not None

    def test_create_auth_and_delete_user(self):
        from django.contrib.auth.models import User
        import uuid
        from django.contrib import auth
        name = str(uuid.uuid4())[:20]
        passwd = str(uuid.uuid4())[:20]
        mail = "none@example.com"
        user = User.objects.create_user(name, mail, passwd)
        user.save()

        auth_user = auth.authenticate(username=name, password=passwd)
        assert auth_user is not None

        user = User.objects.get(username=name)
        assert user is not None

        User.objects.get(username=name).delete()
        try:
            err = User.objects.get(username=name)
        except Exception:
            err = None
        assert err is None


#USE OF HELPER CLS HERE IS SAFE

class TestPath(object):

    def test_windows_path_to_linux_for_ffmpeg_path(self):
        assert VR.to_linux_translate('C:\_USERS\lol', 'tester') == '/home/stepic/VIDEO/STEPICSTUDIO/tester/'


TestHelper = Helper()
TestHelper.create_test_user(force_rewrite=True)
from stepicstudio.models import CameraStatus


class TestRecordings(object):

    def test_start_recording(self):
        request_args = TestHelper.helper_data
        status = VR.start_recording(**request_args)
        assert status

    def test_recording_status(self):
        db_camera = CameraStatus.objects.get(id="1")
        assert db_camera.status == True

    def test_stop_recording(self):
        VR.stop_cam_recording()

    def test_is_recording_stoped(self):
        db_camera = CameraStatus.objects.get(id="1")
        assert db_camera.status == False

class TestCleaner(object):

    def test_delete_all_tmp_data(self):
        assert TestHelper.clean_all_test_objects() == True

# TestHelper.clean_all_test_objects()
