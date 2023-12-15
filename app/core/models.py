from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal, DivisionByZero
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

    # Additional custom properties
    is_prime_user = models.BooleanField(default=False)

    objects = KeiboUserManager()

    USERNAME_FIELD = 'email'  # is intrinsically required
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class AssetCategory(models.TextChoices):
    CASH = 'cash'  # is currency
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
    return generate_random_string(prefix='wallet_')


class Wallet(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    # custom name of the wallet
    name = models.CharField(max_length=200, default=default_wallet_name)
    # current asset
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='%(class)s_asset'
    )
    # name of the financial institution or the trademark of the personal wallet provider
    provider = models.CharField(
        max_length=48,
        default='',
    )
    # current balance
    balance = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class WalletPNLTracker(models.Model):
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='%(class)s_wallet'
    )
    # the asset that's been traded to acquire the wallet's asset (ex: usd, eur...)
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='%(class)s_asset'
    )
    # current total amount of the counterparty asset traded to acquire the current asset
    input_amount = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )
    # average purchase price
    average_purchase_ratio = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal('0.00')
    )

    def save(self, *args, **kwargs):
        try:
            # Ensure wallet's balance is not zero to avoid division by zero
            if self.wallet.balance != Decimal('0.00'):
                self.average_purchase_ratio = self.input_amount / self.wallet.balance
            else:
                # Handle the case where balance is zero, if applicable
                # For example, set it to default or perform another calculation
                self.average_purchase_ratio = Decimal('0.00')
        except DivisionByZero:
            self.average_purchase_ratio = Decimal('0.00')

        super(WalletPNLTracker, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.wallet.name} - {self.asset}'


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
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='%(class)s_wallet'
    )
    # Self-referential ForeignKey
    # If exists, it means that this transaction depends on another (transfer for example)
    origin = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transaction_of_origin',
    )
    executed_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=32)  # tax, gas, etc...
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=19, decimal_places=8)
    tags = ArrayField(models.CharField(max_length=24), default=list, blank=True)


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
