# Generated by Django 2.2.12 on 2020-08-15 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LowerThird', '0012_auto_20200801_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scene',
            name='line2',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
