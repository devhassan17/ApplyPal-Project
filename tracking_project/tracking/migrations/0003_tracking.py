# Generated by Django 5.1.3 on 2024-11-20 12:07

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=10)),
                ('ip_address', models.GenericIPAddressField()),
                ('country', models.CharField(default='Unknown', max_length=255)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_records', to='tracking.university')),
            ],
        ),
    ]
