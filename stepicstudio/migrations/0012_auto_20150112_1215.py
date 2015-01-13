# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0011_camerastatus_start_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('from_step', models.BigIntegerField(default=0)),
                ('from_step_uuid', models.BigIntegerField(default=0)),
                ('started', models.BigIntegerField(default=1421064936797)),
                ('duration', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421064936795),
            preserve_default=True,
        ),
    ]
