# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0026_auto_20150113_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='substep',
            name='duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='course',
            name='editors',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='substep',
            name='start_time',
            field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
            preserve_default=True,
        ),
    ]
