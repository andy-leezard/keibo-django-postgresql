from core.lib.supabase.supa_client import supa_client
from os import getenv


def update_asset(id: str, exchange_rate):
    if getenv("USE_SUPABASE_PLUGIN") != "True":
        return
    supa_client.table("asset").update({"usd_exchange_rate": exchange_rate}).eq(
        "id", id
    ).execute()
