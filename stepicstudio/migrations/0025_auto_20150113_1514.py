# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0024_auto_20150113_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=stepicstudio.models.set_time_milisec),
            preserve_default=True,
        ),
    ]
