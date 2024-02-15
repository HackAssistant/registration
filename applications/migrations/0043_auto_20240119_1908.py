# Generated by Django 3.2.23 on 2024-01-19 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0042_auto_20240110_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hackerapplication',
            name='graduation_year',
            field=models.IntegerField(choices=[(2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029')], default=2025),
        ),
        migrations.AlterField(
            model_name='mentorapplication',
            name='graduation_year',
            field=models.IntegerField(choices=[(2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029')], default=2025),
        ),
        migrations.AlterField(
            model_name='volunteerapplication',
            name='graduation_year',
            field=models.IntegerField(choices=[(2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029')], default=2025),
        ),
    ]
