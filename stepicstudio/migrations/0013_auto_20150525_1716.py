# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0012_auto_20150525_1706'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='StatInfo',
        #     fields=[
        #         ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
        #         ('substep', models.BigIntegerField(default=0)),
        #         ('substep_uuid', models.BigIntegerField(default=0)),
        #         ('duration', models.IntegerField(default=0)),
        #     ],
        #     options={
        #     },
        #     bases=(models.Model,),
        # ),
        # migrations.AddField(
        #     model_name='step',
        #     name='start_time',
        #     field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
        #     preserve_default=True,
        # ),
        # migrations.AddField(
        #     model_name='substep',
        #     name='start_time',
        #     field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
        #     preserve_default=True,
        # ),
    ]
