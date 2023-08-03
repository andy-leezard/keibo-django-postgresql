from rest_framework import serializers
from .models import WalletUser, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'balance', 'asset_id']


class WalletUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = ['id', 'wallet', 'role', 'granted_at']
