from rest_framework import serializers
from .models import KeiboUser, WalletUser, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id',
            'provider',
            'category',
            'asset_id',
            'balance',
            'name',
            'is_public',
        ]


class WalletUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = ['id', 'wallet', 'role', 'granted_at']


class KeiboUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeiboUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'objects',
        ]
