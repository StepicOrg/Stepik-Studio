# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0010_camerastatus_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='camerastatus',
            name='start_time',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
    ]
