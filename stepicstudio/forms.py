import os

from django import forms
from django.core.exceptions import ValidationError

from stepicstudio.models import Lesson, Course, Step, SubStep
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

        self.fields['from_courseName'] = forms.ChoiceField(
            choices=get_my_courses(self.user), initial=Course.objects.filter(id=self.from_course)[0].id)

    class Meta:
        model = Lesson
        labels = {'name': 'Enter lesson name', }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Please use meaningful names', 'autofocus': 'autofocus'}),
        }
        exclude = ('from_course', 'position', 'start_time')

    def lesson_save(self):
        ls = self.save()
        ls.save()
        return ls

    def clean(self):
        if Lesson.objects.filter(from_course=self.data['from_courseName'], name=self.cleaned_data.get('name')).count():
            raise ValidationError('Name \'{}\' already exists. Please, use another name for lesson.'
                                  .format(self.cleaned_data.get('name')))

        course = Course.objects.get(id=self.data['from_courseName'])
        new_lesson_path = course.os_path + translate_non_alphanumerics(self.cleaned_data.get('name')) + '/'

        if os.path.isdir(new_lesson_path):
            raise ValidationError('OS already contains directory for lesson \'{}\'. '
                                  'Please, use another name for lesson.'
                                  .format(self.cleaned_data.get('name')))


class StepForm(forms.ModelForm):
    def __init__(self, userId, lessonId, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        self.user = userId
        self.lessonId = lessonId
        self.fields['from_lessonId'] = forms.ChoiceField(choices={(lessonId, "This lesson")})

    class Meta:
        model = Step
        labels = {'name': 'Enter step name', }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Please use meaningful names', 'autofocus': 'autofocus'}),
        }
        exclude = ('from_lesson', 'position', 'start_time', 'duration', 'is_fresh', 'text_data')

    def step_save(self):
        ls = self.save()
        ls.save()
        return ls

    def clean(self):
        if Step.objects.filter(from_lesson=self.lessonId, name=self.cleaned_data.get('name')).count():
            raise ValidationError('Name \'{}\' already exists. Please, use another name for step.'
                                  .format(self.cleaned_data.get('name')))

        lesson = Lesson.objects.get(id=self.lessonId)
        new_step_path = lesson.os_path + translate_non_alphanumerics(self.cleaned_data.get('name')) + '/'

        if os.path.isdir(new_step_path):
            raise ValidationError('OS already contains directory for step \'{}\'. Please, use another name for step.'
                                  .format(self.cleaned_data.get('name')))
