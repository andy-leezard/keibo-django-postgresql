# Generated by Django 4.2.1 on 2023-08-03 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_walletuser_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='walletuser',
            name='role',
            field=models.IntegerField(choices=[(1, 'Viewer'), (2, 'Editor'), (3, 'Manager'), (4, 'Owner')]),
        ),
    ]