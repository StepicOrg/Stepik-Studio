# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import stepicstudio.models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0020_auto_20181106_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='start_time',
            field=models.BigIntegerField(default=0),
        ),
    ]
