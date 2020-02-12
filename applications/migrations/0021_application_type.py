# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-09 12:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0020_auto_20200206_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='type',
            field=models.CharField(choices=[('V', 'Volunteer'), ('H', 'Hacker'), ('M', 'Mentor'), ('S', 'Sponsor')], default='H', max_length=2),
        ),
    ]
