import os

from django import forms
from django.core.exceptions import ValidationError

from stepicstudio.models import Lesson, Course, Step
from stepicstudio.utils.extra import translate_non_alphanumerics


def get_my_courses(userId):
    courses = Course.objects.filter(editors=userId)
    result = set()
    for i, C in enumerate(courses):
        result.add((C.id, C))
    return result


class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('userId')
        self.from_course = kwargs.pop('from_course', 1)
        super(LessonForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Lesson
        labels = {'name': 'Enter lesson name', }
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Lesson name',
                                                  'autofocus': 'autofocus',
                                                  'required': 'required',
                                                  'class': 'form-control'})}

        exclude = ('from_course', 'position', 'start_time')

    def lesson_save(self):
        ls = self.save()
        ls.save()
        return ls

    def clean(self):
        if not self.cleaned_data.get('name'):
            return

        if Lesson.objects.filter(from_course=self.from_course, name=self.cleaned_data.get('name')).exists():
            raise ValidationError('Name \'{}\' already exists. Please, use another name for lesson.'
                                  .format(self.cleaned_data.get('name')))

        course = Course.objects.get(id=self.from_course)
        new_lesson_path = course.os_path + translate_non_alphanumerics(self.cleaned_data.get('name')) + '/'

        if os.path.isdir(new_lesson_path):
            raise ValidationError('OS already contains directory for lesson \'{}\'. '
                                  'Please, use another name for lesson.'
                                  .format(self.cleaned_data.get('name')))


class StepForm(forms.ModelForm):
    def __init__(self, lesson_id, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        self.lesson_id = lesson_id

    class Meta:
        model = Step
        labels = {'name': 'Enter step name', }
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Step name',
                                                  'autofocus': 'autofocus',
                                                  'required': 'required',
                                                  'class': 'form-control'})}

        exclude = ('from_lesson', 'position', 'start_time', 'duration', 'is_fresh', 'text_data')

    def step_save(self):
        ls = self.save()
        ls.save()
        return ls

    def clean(self):
        if not self.cleaned_data.get('name'):
            return

        if Step.objects.filter(from_lesson=self.lesson_id, name=self.cleaned_data.get('name')).exists():
            raise ValidationError('Name \'{}\' already exists. Please, use another name for step.'
                                  .format(self.cleaned_data.get('name')))

        lesson = Lesson.objects.get(id=self.lesson_id)
        new_step_path = lesson.os_path + translate_non_alphanumerics(self.cleaned_data.get('name')) + '/'

        if os.path.isdir(new_step_path):
            raise ValidationError('OS already contains directory for step \'{}\'. Please, use another name for step.'
                                  .format(self.cleaned_data.get('name')))
