# Generated by Django 3.1.3 on 2020-12-13 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LowerThird', '0016_auto_20201213_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
