# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0007_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400)),
                ('from_step', models.BigIntegerField(default=0)),
                ('position', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='clientFilesFolder',
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='clientIP',
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='recordScreen',
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='recordVideo',
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='serverFilesFolder',
        ),
        migrations.RemoveField(
            model_name='usersettings',
            name='serverIP',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(unique=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
