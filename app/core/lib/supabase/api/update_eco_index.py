from core.lib.supabase.supa_client import supa_client
import copy
import logging
from os import getenv

logger = logging.getLogger(__name__)


def update_eco_index(kwargs):
    if getenv("USE_SUPABASE_PLUGIN") != "True":
        return
    serializable_kwargs = copy.copy(kwargs)
    if "value" in serializable_kwargs:
        serializable_kwargs["value"] = float(serializable_kwargs["value"])
    if "daily_delta" in serializable_kwargs:
        serializable_kwargs["daily_delta"] = float(serializable_kwargs["daily_delta"])
    if "weekly_delta" in serializable_kwargs:
        serializable_kwargs["weekly_delta"] = float(serializable_kwargs["weekly_delta"])
    if "monthly_delta" in serializable_kwargs:
        serializable_kwargs["monthly_delta"] = float(
            serializable_kwargs["monthly_delta"]
        )
    if "yearly_delta" in serializable_kwargs:
        serializable_kwargs["yearly_delta"] = float(serializable_kwargs["yearly_delta"])
    if "decennial_delta" in serializable_kwargs:
        serializable_kwargs["decennial_delta"] = float(
            serializable_kwargs["decennial_delta"]
        )
    supa_client.table("economic_index").upsert(serializable_kwargs).execute()
