# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0028_step_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_visit',
            field=models.DateTimeField(default='2000-10-25 14:30'),
            preserve_default=True,
        ),
    ]
