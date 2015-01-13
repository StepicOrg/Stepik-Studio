# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0013_auto_20150112_1252'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statinfo',
            old_name='from_step',
            new_name='substep',
        ),
        migrations.RenameField(
            model_name='statinfo',
            old_name='from_step_uuid',
            new_name='substep_uuid',
        ),
        migrations.AlterField(
            model_name='statinfo',
            name='started',
            field=models.BigIntegerField(default=1421067777501),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421067777499),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='substep',
            name='start_time',
            field=models.BigIntegerField(default=1421067777499),
            preserve_default=True,
        ),
    ]
