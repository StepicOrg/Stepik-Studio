# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0014_step_is_fresh'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='text_data',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
