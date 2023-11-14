from django.contrib import admin
from .models import (
    KeiboUser,
    Wallet,
    WalletUser,
    Transaction,
    Asset,
    EconomicIndex,
)

admin.site.register(KeiboUser)


@admin.register(EconomicIndex)
class EconomicIndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'value']
    search_fields = ['id']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'exchange_rate']
    list_filter = ['category']
    search_fields = ['id']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'asset',
        'provider',
        'balance',
        'is_public',
    ]
    list_filter = ['asset', 'is_public']
    search_fields = ['name']


@admin.register(WalletUser)
class WalletUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'wallet', 'role', 'granted_at']
    list_filter = ['role']
    raw_id_fields = ['wallet']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'wallet',
        'executed_at',
        'settled_at',
        'category',
        'amount',
        'disposable'
    ]
    list_filter = ['executed_at']
    search_fields = ['wallet__name']
    raw_id_fields = ['wallet']
