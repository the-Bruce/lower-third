# Generated by Django 3.0.6 on 2020-05-20 19:00

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('LowerThird', '0004_remove_scene_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(default='ehFwN', max_length=5)),
                ('date', models.DateField(default=datetime.datetime(2020, 5, 20, 19, 0, 23, 960323, tzinfo=utc))),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='LowerThird.Program')),
                ('scene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='LowerThird.Scene')),
            ],
        ),
    ]
