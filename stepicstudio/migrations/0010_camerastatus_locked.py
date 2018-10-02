# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stepicstudio', '0009_camerastatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400)),
                ('from_step', models.BigIntegerField(default=0)),
                ('position', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
