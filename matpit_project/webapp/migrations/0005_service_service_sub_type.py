# Generated by Django 3.2.7 on 2021-10-04 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_auto_20211004_0440'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='service_sub_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]