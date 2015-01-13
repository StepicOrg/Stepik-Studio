# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0025_auto_20150113_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substep',
            name='start_time',
            field=models.BigIntegerField(default=1421162318932),
            preserve_default=True,
        ),
    ]
