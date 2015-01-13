# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0012_auto_20150112_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='substep',
            name='start_time',
            field=models.BigIntegerField(default=1421067156664),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='statinfo',
            name='started',
            field=models.BigIntegerField(default=1421067156666),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='step',
            name='start_time',
            field=models.BigIntegerField(default=1421067156664),
            preserve_default=True,
        ),
    ]
