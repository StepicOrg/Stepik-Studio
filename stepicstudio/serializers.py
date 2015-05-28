from django.contrib.auth.models import User
from stepicstudio.models import SubStep
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


class SubstepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubStep
        fields = ('name', 'from_step', 'position', 'start_time', 'duration',
                  'screencast_duration', 'os_path_all_variants', )