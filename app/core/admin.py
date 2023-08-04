from django.contrib import admin
from .models import KeiboUser, Wallet, WalletUser, Transaction

admin.site.register(KeiboUser)


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
    list_display = ['wallet', 'user', 'role', 'granted_at']  # 'user' , 'invited_by'
    list_filter = ['role']
    raw_id_fields = ['wallet']  # 'user', 'invited_by'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'beneficiary',
        'donor',
        'amount',
        'date',
        'description',
        'confirmed_by_beneficiary',
        'confirmed_by_donor',
    ]  # 'added_by'
    list_filter = ['confirmed_by_beneficiary', 'confirmed_by_donor']
    search_fields = ['beneficiary__name', 'donor__name', 'description']
    raw_id_fields = ['beneficiary', 'donor']  # 'added_by'
