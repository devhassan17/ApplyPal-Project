# Generated by Django 5.1.3 on 2024-11-20 19:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_userprofile_uni_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='university',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='tracking.university'),
            preserve_default=False,
        ),
    ]