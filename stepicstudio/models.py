from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from stepicstudio.utils.extra import translate_non_alphanumerics
from stepicstudio.const import COURSE_ULR_NAME, STEP_URL_NAME, SUBSTEP_URL_NAME, LESSON_URL_NAME, SUBSTEP_PROFESSOR
import time

# Create your models here.


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

    def __str__(self):
        return self.name + " from lesson id =" + str(self.from_lesson)

    @property
    def os_path(self):
        lesson = Lesson.objects.all().get(id=self.from_lesson)
        return lesson.os_path + translate_non_alphanumerics(self.name) + "/"


class SubStep(models.Model):

    name = models.CharField(max_length=400)
    from_step = models.BigIntegerField(default=0)
    position = models.SmallIntegerField(default=0)
    start_time = models.BigIntegerField(default=set_time_milisec)

    def __str__(self):
        return self.name + " from step id =" + str(self.from_step)

    @property
    def os_path(self):
        step = Step.objects.all().get(id=self.from_step)
        return step.os_path + translate_non_alphanumerics(self.name) + "/" + SUBSTEP_PROFESSOR


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    serverIP = models.CharField(max_length=50)
    clientIP = models.CharField(max_length=50)
    serverFilesFolder = models.CharField(max_length=10000)
    clientFilesFolder = models.CharField(max_length=10000)
    recordVideo = models.BooleanField(default=True)
    recordScreen = models.BooleanField(default=True)


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

