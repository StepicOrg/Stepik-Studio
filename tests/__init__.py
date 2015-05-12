import pytest
import os
from django.test import TestCase

os.environ['DJANGO_SETTINGS_MODULE'] = 'STEPIC_STUDIO.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from stepicstudio.models import UserProfile, Course, Lesson, Step, SubStep, CameraStatus
from STEPIC_STUDIO.settings import TEST_SSH_ACC_USERNAME, TEST_SSH_ACC_PASS


class Helper(object):

    def __init__(self):
        self.helper_data = {}
        self.record_data = {}
        self.created_obj = {}

    def create_test_course_structure(self, force_rewrite=True):
        if not Course.objects.filter(id=8888).exists() and not Lesson.objects.filter(id=8888188).exists() and\
                not Step.objects.filter(id=888818888).exists() and not SubStep.objects.filter(id=888818888) or force_rewrite:
            course = Course(id=8888, name="Test_Course8888", start_date='2036-01-01 04:20')
            lesson = Lesson(id=8888188, name="Test_Lesson8888188", from_course=8888)
            step = Step(id=888818888, name="Test_Step888818888", from_lesson=8888188)
            substep = SubStep(id=888818888, name="Step1from888818888", from_step=888818888)
            course.save()
            lesson.save()
            step.save()
            substep.save()
            self.created_obj.update({'Course': course, 'Lesson': lesson, 'Step': step, 'currSubStep': substep})

    def create_local_machine_ssh(self):
        self.helper_data.update({'remote_ubuntu': {
            'professor_ip': 'localhost',
            'ubuntu_username': TEST_SSH_ACC_USERNAME,
            'ubuntu_password': TEST_SSH_ACC_PASS,
            'ubuntu_folder_path':'/Users/mehanig/CODE/STEPIC_STUDIO',
        }})

    def create_test_user(self, force_rewrite=True):
        if not self.helper_data:
            from django.contrib.auth.models import User
            import uuid
            name = str(uuid.uuid4())[:20]
            passwd = str(uuid.uuid4())[:20]
            mail = "none@example.com"
            user = User.objects.create_user(name, mail, passwd)
            user.save()
            user_profile = UserProfile(user)
            user_profile.serverFilesFolder = './__TEMP_FOLDER__'
            user_id = user.id
            if not self.record_data:
                self.create_test_course_structure(force_rewrite)
                self.create_local_machine_ssh()
            self.helper_data.update({'username': name,
                                     'user_email': mail,
                                     'userpasswd': passwd,
                                     'user_id': user_id,
                                     'user_profile': user_profile,
                                     'data': self.created_obj, })
            self.created_obj.update({'user': user})


    def clean_all_test_objects(self):
        for key, obj in self.created_obj.items():
            obj.delete()