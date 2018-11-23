# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-17 09:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0029_application_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='other_gender',
        ),
        migrations.AlterField(
            model_name='application',
            name='gender',
            field=models.CharField(choices=[('NA', 'Prefer not to answer'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='NA', max_length=20),
        ),
    ]