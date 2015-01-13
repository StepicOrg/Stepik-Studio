# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0003_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='position',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
