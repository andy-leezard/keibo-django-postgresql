from django.contrib import admin
from .models import KeiboUser, Wallet, WalletUser, Transaction, Asset, EconomicIndex

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
        'provider',
        'category',
        'asset_id',
        'balance',
        'name',
        'is_public',
    ]
    list_filter = ['category', 'is_public']
    search_fields = ['name']


@admin.register(WalletUser)
class WalletUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'wallet', 'role', 'granted_at']
    list_filter = ['role']
    raw_id_fields = ['wallet']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'recipient',
        'sender',
        'date',
        'description',
        'confirmed_by_recipient',
    ]  # 'added_by'
    list_filter = ['confirmed_by_recipient']
    search_fields = ['recipient__name', 'sender__name', 'description']
    raw_id_fields = ['recipient', 'sender']  # 'added_by'
