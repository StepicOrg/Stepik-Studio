# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0013_auto_20150525_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='is_fresh',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
