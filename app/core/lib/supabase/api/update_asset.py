from core.lib.supabase.supa_client import supa_client


def update_asset(id: str, exchange_rate):
    supa_client.table("asset").update({"usd_exchange_rate": exchange_rate}).eq(
        "id", id
    ).execute()
