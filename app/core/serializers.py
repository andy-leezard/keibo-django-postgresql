from rest_framework import serializers
from .models import KeiboUser, WalletUser, Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            'id',
            'provider',
            'category',
            'asset_id',
            'balance',
            'name',
            'icon',
            'is_public',
        ]

    def get_balance(self, obj):
        return float(obj.balance)


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
    date = serializers.SerializerMethodField()
    gross_amount = serializers.SerializerMethodField()
    net_amount = serializers.SerializerMethodField()
    transaction_fee = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'category',
            'recipient',
            'sender',
            'confirmed_by_recipient',
            'confirmed_by_sender',
            'gross_amount',
            'net_amount',
            'transaction_fee',
            'description',
            'date',
        ]

    def get_date(self, obj):
        return int(obj.date.timestamp() * 1000)

    def get_gross_amount(self, obj):
        return float(obj.gross_amount)

    def get_net_amount(self, obj):
        return float(obj.net_amount)

    def get_transaction_fee(self, obj):
        return float(obj.transaction_fee)
