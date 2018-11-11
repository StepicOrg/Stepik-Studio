# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0019_auto_20181106_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substep',
            name='duration',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='substep',
            name='screencast_duration',
            field=models.FloatField(default=0.0),
        ),
    ]
