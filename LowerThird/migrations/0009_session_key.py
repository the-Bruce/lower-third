# Generated by Django 2.2.12 on 2020-05-22 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LowerThird', '0008_auto_20200521_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='key',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]