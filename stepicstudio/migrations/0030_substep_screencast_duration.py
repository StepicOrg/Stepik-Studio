# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0029_userprofile_last_visit'),
    ]

    operations = [
        migrations.AddField(
            model_name='substep',
            name='screencast_duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
    ]
