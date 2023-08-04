from rest_framework import serializers
from .models import WalletUser, Wallet


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
