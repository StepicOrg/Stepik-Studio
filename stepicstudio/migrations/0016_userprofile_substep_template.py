# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0015_step_text_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='substep_template',
            field=models.CharField(max_length=120, default='SubStep$idfrom$stepid'),
            preserve_default=True,
        ),
    ]
