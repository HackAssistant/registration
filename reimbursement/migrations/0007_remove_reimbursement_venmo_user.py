# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-23 11:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursement', '0006_auto_20181122_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reimbursement',
            name='venmo_user',
        ),
    ]