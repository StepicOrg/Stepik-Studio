# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0005_step'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('serverIP', models.CharField(max_length=50)),
                ('clientIP', models.CharField(max_length=50)),
                ('serverFilesFolder', models.CharField(max_length=10000)),
                ('clientFilesFolder', models.CharField(max_length=10000)),
                ('recordVideo', models.BooleanField(default=True)),
                ('recordScreen', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
