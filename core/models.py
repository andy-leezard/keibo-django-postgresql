from django.db import models
from django.contrib.auth.models import AbstractUser
import decimal

class OAuthUser(AbstractUser):
    pass

class AssetCategory(models.TextChoices):
    CASH = 'cash'
    EQUITY = 'equity'
    CRYPTO = 'crypto'
    FUND = 'fund'
    OTHER = 'other'

WALLET_TYPE_CHOICES = [
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Private'),
]

class Wallet(models.Model):
    asset_id = models.CharField(max_length=24)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=AssetCategory.choices)
    balance = models.DecimalField(max_digits=19, decimal_places=8, default=decimal.Decimal('0.00'))
    wallet_type = models.CharField(max_length=7, choices=WALLET_TYPE_CHOICES)

    def __str__(self):
        return self.name

ROLES = [
    (1, 'Viewer'),
    (2, 'Editor'),
    (3, 'Manager'),
    (4, 'Admin'),
]

class WalletUser(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='wallet_users')
    user = models.ForeignKey(OAuthUser, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLES)
    granted_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(OAuthUser, on_delete=models.SET_NULL, null=True, related_name='invitations')

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=19, decimal_places=8)
    date = models.DateTimeField(auto_now_add=True)
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200, blank=True)
    added_by = models.ForeignKey(OAuthUser, on_delete=models.CASCADE)
