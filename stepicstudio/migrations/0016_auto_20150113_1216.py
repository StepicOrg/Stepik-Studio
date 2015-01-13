# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0015_auto_20150112_1318'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserSettings',
        ),
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421151389009),
            preserve_default=True,
        ),
    ]
