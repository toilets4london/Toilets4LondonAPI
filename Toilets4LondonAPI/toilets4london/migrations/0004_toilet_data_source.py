# Generated by Django 3.1.1 on 2020-10-16 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toilets4london', '0003_auto_20200930_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='toilet',
            name='data_source',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
