from django.contrib import admin
from .models import OAuthUser, Wallet, WalletUser, Transaction

admin.site.register(OAuthUser)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['name', 'balance', 'asset_id', 'name', 'category', 'wallet_type']
    search_fields = ['name']

@admin.register(WalletUser)
class WalletUserAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'user', 'role', 'granted_at', 'invited_by']
    list_filter = ['role']
    raw_id_fields = ['wallet', 'user', 'invited_by']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'date', 'type', 'added_by']
    list_filter = ['type']
    search_fields = ['wallet__name', 'description']
    raw_id_fields = ['wallet', 'added_by']
