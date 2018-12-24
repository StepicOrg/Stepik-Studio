import datetime
import time

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.timezone import utc

from stepicstudio.const import *
from stepicstudio.utils.extra import translate_non_alphanumerics, file_exist


def set_time_milisec():
    return int(time.time() * 1000)


class Course(models.Model):
    name = models.CharField(max_length=200)
    editors = models.SmallIntegerField(default=0)
    start_date = models.DateTimeField('Start date of course')

    def __str__(self):
        return self.name + ' ' + str(self.start_date)

    @property
    def os_path(self):
        user_id = self.editors
        user_folder = UserProfile.objects.get(user_id=user_id)\
            .serverFilesFolder\
            .replace('/', os.sep)  # DB may contain path with bad separators
        return os.path.join(user_folder, translate_non_alphanumerics(self.name) + os.sep)

    @property
    def os_automontage_path(self):
        user_id = self.editors
        user_folder = UserProfile.objects.get(user_id=user_id).serverFilesFolder
        return os.path.join(user_folder, RAW_CUT_FOLDER_NAME, translate_non_alphanumerics(self.name) + os.sep)

    @property
    def tablet_path(self):
        user_id = self.editors
        username = User.objects.get(id=user_id).username
        return settings.LINUX_DIR + username + '/' + translate_non_alphanumerics(self.name) + '/'

    @property
    def url(self):
        return '/' + COURSE_ULR_NAME + '/' + str(self.id) + '/'


class Lesson(models.Model):
    name = models.CharField(max_length=400)
    from_course = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)

    def __str__(self):
        return self.name + ' from course id =' + str(self.from_course)

    @property
    def url(self):
        course = Course.objects.get(id=self.from_course)
        return '/' + COURSE_ULR_NAME + '/' + str(course.id) + '/' + LESSON_URL_NAME + '/' + str(self.id) + '/'

    @property
    def os_path(self):
        course = Course.objects.get(id=self.from_course)
        return course.os_path + translate_non_alphanumerics(self.name) + os.sep

    @property
    def os_automontage_path(self):
        course = Course.objects.get(id=self.from_course)
        return course.os_automontage_path + translate_non_alphanumerics(self.name) + os.sep

    @property
    def tablet_path(self):
        course = Course.objects.get(id=self.from_course)
        return course.tablet_path + translate_non_alphanumerics(self.name) + '/'


class Step(models.Model):
    name = models.CharField(max_length=400)
    from_lesson = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)
    duration = models.BigIntegerField(default=0)
    is_fresh = models.BooleanField(default=False)
    text_data = models.TextField(default='')

    def __str__(self):
        return self.name + ' from lesson id =' + str(self.from_lesson)

    @property
    def os_path(self):
        lesson = Lesson.objects.get(id=self.from_lesson)
        return lesson.os_path + translate_non_alphanumerics(self.name) + os.sep

    @property
    def os_automontage_path(self):
        lesson = Lesson.objects.get(id=self.from_lesson)
        return lesson.os_automontage_path + translate_non_alphanumerics(self.name) + os.sep

    @property
    def tablet_path(self):
        lesson = Lesson.objects.get(id=self.from_lesson)
        return lesson.tablet_path + translate_non_alphanumerics(self.name) + '/'


class SubStep(models.Model):
    name = models.CharField(max_length=400)
    from_step = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)
    duration = models.FloatField(default=0.0)
    screencast_duration = models.FloatField(default=0.0)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ' from step id =' + str(self.from_step)

    @property
    def camera_recording_name(self):
        return self.name + SUBSTEP_PROFESSOR

    @property
    def screencast_name(self):
        return self.name + SUBSTEP_SCREEN

    @property
    def dir_path(self):
        return Step.objects.get(id=self.from_step).os_path

    @property
    def os_path(self):
        return os.path.join(Step.objects.get(id=self.from_step).os_path, self.camera_recording_name)

    # allows users to view files which recorded with previous version of studio
    @property
    def os_path_old(self):
        step = Step.objects.get(id=self.from_step)
        return os.path.join(step.os_path + translate_non_alphanumerics(self.name), self.camera_recording_name)

    @property
    def os_screencast_path(self):
        return os.path.join(Step.objects.get(id=self.from_step).os_path, self.screencast_name)

    # allows users to view files which recorded with previous version of studio
    @property
    def os_screencast_path_old(self):
        step = Step.objects.get(id=self.from_step)
        return os.path.join(step.os_path + translate_non_alphanumerics(self.name), self.screencast_name)

    @property
    def os_tablet_dir(self):
        return Step.objects.get(id=self.from_step).tablet_path

    @property
    def os_tablet_path(self):
        return Step.objects.get(id=self.from_step).tablet_path + self.screencast_name

    @property
    def is_videos_ok(self):
        return self.screencast_duration - self.duration < 7 and self.screencast_duration > 0 and self.duration > 0

    @property
    def os_automontage_path(self):
        return Step.objects.get(id=self.from_step).os_automontage_path

    @property
    def os_automontage_file(self):
        return os.path.join(self.os_automontage_path, self.name + RAW_CUT_POSTFIX)

    @property
    def automontage_exist(self):
        return file_exist(self.os_automontage_file)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    last_visit = models.DateTimeField(default='2000-10-25 14:30')
    serverIP = models.CharField(max_length=50)
    clientIP = models.CharField(max_length=50)
    serverFilesFolder = models.CharField(max_length=10000)
    clientFilesFolder = models.CharField(max_length=10000)
    recordVideo = models.BooleanField(default=True)
    recordScreen = models.BooleanField(default=True)
    substep_template = models.CharField(max_length=120, default='Step$id_part$stepid')

    @property
    def is_ready_to_show_hello_screen(self) -> True | False:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.last_visit
        if timediff.total_seconds() > 60 * 60 * 12:
            return True
        return False


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# Some magic here?
post_save.connect(create_user_profile, sender=User)


class CameraStatus(models.Model):
    status = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    start_time = models.BigIntegerField(default=0)


class StatInfo(models.Model):
    substep = models.BigIntegerField(default=0)
    substep_uuid = models.BigIntegerField(default=0)
    duration = models.IntegerField(default=0)
