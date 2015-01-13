# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0014_auto_20150112_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statinfo',
            name='started',
        ),
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421068706799),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='substep',
            name='start_time',
            field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
            preserve_default=True,
        ),
    ]
