# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0016_userprofile_substep_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='substep',
            name='is_locked',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
