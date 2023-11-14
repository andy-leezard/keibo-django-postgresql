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
    # custom name of the wallet
    name = models.CharField(max_length=200, default=default_wallet_name)
    # current asset
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='%(class)s_asset')
    # the other asset that's been traded to acquire the current asset (ex: usd, eur...)
    # (Only used to measure PNL)
    input_asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='%(class)s_input_asset', blank=True)
    # name of the financial institution or the trademark of the personal wallet provider
    provider = models.CharField(
        max_length=48,
        default="",
    )
    # current balance
    balance = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )
    # accumulated amount of the counterparty asset traded to acquire the current asset
    # (Only used to measure PNL)
    input_amount = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


ROLES = [
    (1, 'Viewer'),
    (2, 'Editor'),
    (3, 'Manager'),
    (4, 'Owner'),
]


# Used for WalletUser and Invitations
class AbstractWalletReference(models.Model):
    user = models.ForeignKey(
        KeiboUser, on_delete=models.CASCADE, related_name='%(class)s_user'
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='%(class)s_wallet'
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
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='%(class)s_wallet')
    executed_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=32)  # tax, gas, etc...
    # to whom (or from whom) ?
    counterparty = models.CharField(max_length=256)  # tax, gas, etc...
    # description
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=19, decimal_places=8)
    # means the expense was avoidable - was charged within the disposable range of income
    disposable = models.BooleanField(default=False)


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
