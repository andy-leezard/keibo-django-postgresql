# Generated by Django 4.2.1 on 2023-08-29 22:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_wallet_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='cross_amount',
            new_name='gross_amount',
        ),
    ]