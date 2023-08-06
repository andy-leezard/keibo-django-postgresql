# Generated by Django 4.2.1 on 2023-08-05 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_wallet_wallet_type_wallet_is_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('exchange_rate', models.DecimalField(decimal_places=12, max_digits=24)),
            ],
        ),
    ]