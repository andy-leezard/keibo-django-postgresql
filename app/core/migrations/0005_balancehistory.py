# Generated by Django 4.2.1 on 2023-11-10 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_asset_icon_remove_asset_symbol'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('old_balance', models.DecimalField(decimal_places=8, max_digits=19)),
                ('new_balance', models.DecimalField(decimal_places=8, max_digits=19)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.wallet')),
            ],
        ),
    ]
