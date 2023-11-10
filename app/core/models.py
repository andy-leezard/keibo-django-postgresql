from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from datetime import date
from decimal import Decimal
import uuid
from .utils import generate_random_string


class KeiboUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(email=email, **kwargs)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email, password=password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class KeiboUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)
    registered_at = models.DateTimeField(default=timezone.now)

    # Djoser needs it false either way.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = KeiboUserManager()

    USERNAME_FIELD = 'email'  # is intrinsically required
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class AssetCategory(models.TextChoices):
    CASH = 'cash'
    EQUITY = 'equity'
    CRYPTO = 'crypto'
    FUND = 'fund'
    OTHER = 'other'


class Asset(models.Model):
    id = models.CharField(max_length=32, unique=True, primary_key=True)
    # asset category
    category = models.CharField(
        max_length=10, choices=AssetCategory.choices, default=AssetCategory.CASH
    )
    # against the USD
    exchange_rate = models.DecimalField(max_digits=24, decimal_places=12)


def default_wallet_name():
    return generate_random_string(prefix="wallet_")


class Wallet(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    # name of the financial institution or the trademark of the personal wallet provider
    provider = models.CharField(
        max_length=48,
        default="",
    )
    # custom name of the wallet
    name = models.CharField(max_length=200, default=default_wallet_name)
    balance = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def update_balance(self, new_balance, reason=None):
        BalanceHistory.objects.create(
            wallet=self,
            old_balance=self.balance,
            new_balance=new_balance,
            reason=reason
        )
        self.balance = new_balance
        self.save()


class BalanceHistory(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_balance = models.DecimalField(max_digits=19, decimal_places=8)
    new_balance = models.DecimalField(max_digits=19, decimal_places=8)

    def __str__(self):
        return f"Balance change for {self.wallet.name} on {self.timestamp}"


ROLES = [
    (1, 'Viewer'),
    (2, 'Editor'),
    (3, 'Manager'),
    (4, 'Owner'),
]


# Used for WalletUser and Invitations
class AbstractWalletReference(models.Model):
    user = models.ForeignKey(
        KeiboUser, on_delete=models.CASCADE, related_name='%(class)s_users'
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='%(class)s_wallets'
    )
    role = models.IntegerField(choices=ROLES)

    class Meta:
        abstract = True


class WalletUser(AbstractWalletReference):
    granted_at = models.DateTimeField(auto_now_add=True)


class Invitation(AbstractWalletReference):
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    category = models.CharField(max_length=32)  # tax, gas, etc...
    recipient = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        related_name='recipient',
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL, related_name='sender', null=True, blank=True
    )
    confirmed_by_recipient = models.BooleanField(default=False)
    confirmed_by_sender = models.BooleanField(default=False)
    gross_amount = models.DecimalField(max_digits=19, decimal_places=8)
    net_amount = models.DecimalField(max_digits=19, decimal_places=8)
    transaction_fee = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal(0)
    )
    date = models.DateTimeField(auto_now_add=True)  # executed_at
    description = models.CharField(max_length=200, blank=True)

    # added_by = models.ForeignKey(OAuthUser, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.recipient is None and self.sender is None:
            self.delete()
        else:
            if self.net_amount + self.transaction_fee != self.gross_amount:
                self.transaction_fee = self.gross_amount - self.net_amount
            super().save(*args, **kwargs)


# Example: S&P 500, crypto total market cap, interest rate, etc...
class EconomicIndex(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    # Delta in percentage
    daily_delta = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    weekly_delta = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    monthly_delta = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    yearly_delta = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    decennial_delta = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
