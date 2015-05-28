# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0011_camerastatus_start_time'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='StatInfo',
        #     fields=[
        #         ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
        #         ('substep', models.BigIntegerField(default=0)),
        #         ('substep_uuid', models.BigIntegerField(default=0)),
        #         ('duration', models.IntegerField(default=0)),
        #     ],
        #     options={
        #     },
        #     bases=(models.Model,),
        # ),
        migrations.DeleteModel(
            name='UserSettings',
        ),
        migrations.AddField(
            model_name='step',
            name='duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
        # migrations.AddField(
        #     model_name='step',
        #     name='start_time',
        #     field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
        #     preserve_default=True,
        # ),
        migrations.AddField(
            model_name='substep',
            name='duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='substep',
            name='screencast_duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
        # migrations.AddField(
        #     model_name='substep',
        #     name='start_time',
        #     field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
        #     preserve_default=True,
        # ),
        migrations.AddField(
            model_name='userprofile',
            name='last_visit',
            field=models.DateTimeField(default='2000-10-25 14:30'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='course',
            name='editors',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
