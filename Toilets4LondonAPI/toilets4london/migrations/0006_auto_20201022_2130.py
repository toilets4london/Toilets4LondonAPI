# Generated by Django 3.1.1 on 2020-10-22 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toilets4london', '0005_auto_20201022_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='toilet',
            name='covid',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='toilet',
            name='fee',
            field=models.CharField(blank=True, default='Free', max_length=100),
        ),
    ]