from django.contrib.auth.models import User
from stepicstudio.models import SubStep, Step
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


class SubstepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStep
        fields = ('id', 'name', 'from_step', 'position', 'start_time', 'duration',
                  'screencast_duration', 'os_path_all_variants', 'screencast_duration')

class StepSerializer(serializers.ModelSerializer):
    substep_list = SubstepSerializer(many=True, read_only=True)

    class Meta:
        model = Step
        fields = ('id', 'name', 'from_lesson', 'position', 'start_time', 'is_fresh', 'text_data', 'substep_list')
