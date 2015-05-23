# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0027_auto_20150522_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='duration',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
    ]
