from rest_framework import serializers
from .models import KeiboUser, WalletUser, Wallet, Transaction, Asset
from decimal import Decimal


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id',
            'category',
            'exchange_rate',
        ]


class BalanceField(serializers.Field):
    def to_representation(self, value):
        return float(value)

    def to_internal_value(self, data):
        return Decimal(data)


class WalletSerializer(serializers.ModelSerializer):
    balance = BalanceField()
    input_amount = BalanceField()

    class Meta:
        model = Wallet
        fields = [
            'id',
            'name',
            'asset',
            'input_asset',
            'provider',
            'balance',
            'input_amount',
            'is_public',
        ]

    def get_balance(self, obj):
        return float(obj.balance)

    def get_input_amount(self, obj):
        return float(obj.input_amount)


class WalletUserSerializer(serializers.ModelSerializer):
    granted_at = serializers.SerializerMethodField()

    class Meta:
        model = WalletUser
        fields = ['id', 'wallet', 'role', 'granted_at']

    def get_granted_at(self, obj):
        return int(obj.date.timestamp() * 1000)


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


class TransactionSerializer(serializers.ModelSerializer):
    executed_at = serializers.SerializerMethodField()
    settled_at = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'wallet',
            'executed_at',
            'settled_at',
            'category',
            'counterparty',
            'description',
            'amount',
            'disposable',
        ]

    def get_executed_at(self, obj):
        return int(obj.executed_at.timestamp() * 1000)

    def get_settled_at(self, obj):
        return int(obj.settled_at.timestamp() * 1000)

    def get_amount(self, obj):
        return float(obj.amount)
