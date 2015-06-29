from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from stepicstudio.utils.extra import translate_non_alphanumerics
from stepicstudio.const import COURSE_ULR_NAME, STEP_URL_NAME, SUBSTEP_URL_NAME, LESSON_URL_NAME, SUBSTEP_PROFESSOR, \
    SUBSTEP_PROFESSOR_v1, SUBSTEP_SCREEN, SUBSTEP_SCREEN_v1
import time, datetime
from django.utils.timezone import utc


def set_time_milisec():
    return int(time.time() * 1000)


class Course(models.Model):
    name = models.CharField(max_length=200)
    editors = models.SmallIntegerField(default=0)
    start_date = models.DateTimeField('Start date of course')

    def __str__(self):
        return self.name + " " + str(self.start_date)

    @property
    def os_path(self):
        user_id = self.editors
        user_folder = UserProfile.objects.all().get(user_id=user_id).serverFilesFolder
        return user_folder + "/" + translate_non_alphanumerics(self.name) + "/"

    @property
    def url(self):
        return "/" + COURSE_ULR_NAME + "/" + str(self.id) + "/"


class Lesson(models.Model):
    name = models.CharField(max_length=400)
    from_course = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name + " from course id =" + str(self.from_course)

    @property
    def url(self):
        course = Course.objects.all().get(id=self.from_course)
        return "/" + COURSE_ULR_NAME + "/" + str(course.id) + "/" + LESSON_URL_NAME + "/" + str(self.id) + "/"

    @property
    def os_path(self):
        course = Course.objects.all().get(id=self.from_course)
        return course.os_path + translate_non_alphanumerics(self.name) + "/"


class Step(models.Model):
    name = models.CharField(max_length=400)
    from_lesson = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)
    duration = models.BigIntegerField(default=0)
    is_fresh = models.BooleanField(default=False)
    text_data = models.TextField(default='')

    def __str__(self):
        return self.name + " from lesson id =" + str(self.from_lesson)

    @property
    def os_path(self):
        lesson = Lesson.objects.all().get(id=self.from_lesson)
        return lesson.os_path + translate_non_alphanumerics(self.name) + "/"


# TODO: use duration in SubStep instead of Step
class SubStep(models.Model):

    name = models.CharField(max_length=400)
    from_step = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)
    duration = models.BigIntegerField(default=0)
    screencast_duration = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name + " from step id =" + str(self.from_step)

    @property
    def os_path(self):
        step = Step.objects.all().get(id=self.from_step)
        return step.os_path + translate_non_alphanumerics(self.name) + "/" + self.name + SUBSTEP_PROFESSOR

    @property
    def os_path_v1(self):
        step = Step.objects.all().get(id=self.from_step)
        return step.os_path + translate_non_alphanumerics(self.name) + "/" + SUBSTEP_PROFESSOR_v1

    @property
    def os_path_all_variants(self):
        return [self.os_path, self.os_path_v1]

    @property
    def os_screencast_path(self):
        step = Step.objects.all().get(id=self.from_step)
        return step.os_path + translate_non_alphanumerics(self.name) + "/" + self.name + SUBSTEP_SCREEN

    @property
    def os_screencast_path_v1(self):
        step = Step.objects.all().get(id=self.from_step)
        return step.os_path + translate_non_alphanumerics(self.name) + "/" + SUBSTEP_SCREEN_v1

    @property
    def os_screencast_path_all_variants(self):
        return [self.os_screencast_path, self.os_screencast_path_v1]

    @property
    def is_videos_ok(self):
        return self.screencast_duration - self.duration < 7 and self.screencast_duration > self.duration > 0


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_visit = models.DateTimeField(default="2000-10-25 14:30")
    serverIP = models.CharField(max_length=50)
    clientIP = models.CharField(max_length=50)
    serverFilesFolder = models.CharField(max_length=10000)
    clientFilesFolder = models.CharField(max_length=10000)
    recordVideo = models.BooleanField(default=True)
    recordScreen = models.BooleanField(default=True)

    @property
    def is_ready_to_show_hello_screen(self) -> True | False:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.last_visit
        if timediff.total_seconds() > 60*60*12:
            return True
        return False


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class CameraStatus(models.Model):
    status = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    start_time = models.BigIntegerField(default=0)


class StatInfo(models.Model):
    substep = models.BigIntegerField(default=0)
    substep_uuid = models.BigIntegerField(default=0)
    duration = models.IntegerField(default=0)
