# Generated by Django 4.2.1 on 2023-11-21 23:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_asset_economicindex_wallet_keibouser_avatar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=24), blank=True, default=list, size=None),
        ),
    ]
