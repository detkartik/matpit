# Generated by Django 3.1.5 on 2021-07-23 03:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_comment_lead_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lead_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lead',
            name='referral_code',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='referred_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
