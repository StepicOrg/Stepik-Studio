# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0022_auto_20150113_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421151626117),
            preserve_default=True,
        ),
    ]
