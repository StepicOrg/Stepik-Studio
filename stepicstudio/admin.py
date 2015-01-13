from django.contrib import admin

# Register your models here.
from stepicstudio.models import Course, Lesson, Step, UserProfile, CameraStatus

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Step)
admin.site.register(UserProfile)
admin.site.register(CameraStatus)