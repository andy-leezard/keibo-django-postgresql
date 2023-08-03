from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
import decimal


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
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)  # Djoser needs it false either way.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = KeiboUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


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
    balance = models.DecimalField(
        max_digits=19, decimal_places=8, default=decimal.Decimal('0.00')
    )
    wallet_type = models.CharField(max_length=7, choices=WALLET_TYPE_CHOICES)

    def __str__(self):
        return self.name


ROLES = [
    (1, 'Viewer'),
    (2, 'Editor'),
    (3, 'Manager'),
    (4, 'Owner'),
]


class WalletUser(models.Model):
    user = models.ForeignKey(KeiboUser, on_delete=models.CASCADE)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='wallet_users'
    )
    # user = models.ForeignKey(OAuthUser, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLES)
    granted_at = models.DateTimeField(auto_now_add=True)
    # invited_by = models.ForeignKey(OAuthUser, on_delete=models.SET_NULL, null=True, related_name='invitations')


class Transaction(models.Model):
    beneficiary = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        related_name='beneficiary',
        null=True,
        blank=True,
    )
    donor = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL, related_name='donor', null=True, blank=True
    )
    confirmed_by_beneficiary = models.BooleanField(default=False)
    confirmed_by_donor = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=19, decimal_places=8)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

    # added_by = models.ForeignKey(OAuthUser, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.beneficiary is None and self.donor is None:
            self.delete()
        else:
            super().save(*args, **kwargs)
