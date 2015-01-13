# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stepicstudio', '0006_usersettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('serverIP', models.CharField(max_length=50)),
                ('clientIP', models.CharField(max_length=50)),
                ('serverFilesFolder', models.CharField(max_length=10000)),
                ('clientFilesFolder', models.CharField(max_length=10000)),
                ('recordVideo', models.BooleanField(default=True)),
                ('recordScreen', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
