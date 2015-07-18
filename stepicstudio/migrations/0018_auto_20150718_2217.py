# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0017_substep_is_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='substep_template',
            field=models.CharField(default='Step$id_part$stepid', max_length=120),
            preserve_default=True,
        ),
    ]
