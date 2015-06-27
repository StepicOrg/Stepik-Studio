from django import forms
from stepicstudio.models import Lesson, Course, Step, SubStep


def get_my_courses(userId):
    courses = Course.objects.all().filter(editors=userId)
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
            choices=get_my_courses(self.user), initial=Course.objects.all().filter(id=self.from_course)[0].id)

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


class StepForm(forms.ModelForm):

    def __init__(self, userId, lessonId, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        self.user = userId
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
