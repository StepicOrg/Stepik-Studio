import pytest
import os
from django.test import TestCase


os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


import stepicstudio.VideoRecorder.action as VR


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


class TestPath(object):

    def test_windows_path_to_linux_for_ffmpeg_path(self):
        assert VR.to_linux_translate('C:\_USERS\lol', 'tester') == '\lola'
        assert VR.to_linux_translate('/_thisIs Bad Path/oop&s.mp4', '\_thisIs Bad Path\oops.mp4' )
