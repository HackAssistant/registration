# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-07 18:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0010_application_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationcomment',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
