# Generated by Django 4.2.1 on 2023-09-02 23:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_wallet_category_alter_asset_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='symbol',
        ),
    ]
