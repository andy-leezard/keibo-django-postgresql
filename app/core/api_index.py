import requests
import logging
from core.models import EconomicIndex
from keibo.settings import API_FRED_KEY
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


def get_past_date_in_yyyy_mm_dd(days: int):
    current_date = datetime.now()
    date_ago = current_date - timedelta(days)
    return date_ago.strftime('%Y-%m-%d')


def get_list_item(list, index):
    if index >= 0:
        return list[index] if len(list) > abs(index) else None
    else:
        return list[index] if len(list) >= abs(index) else None


def str_can_be_decimal(string):
    try:
        Decimal(string)
        return True
    except:
        return False


# FED
FED_FUNDS_RATE_ID = "FEDFUNDS"

# ECB
# Deposit Facility Rate (Floor) - rate at which the ECB pays clients
ECB_DEPOSIT_FACILITY_RATE = "ECBDFR"
# Deposit Facility Rate (Floor) - rate at which clients refinance from the ECB
ECB_MAIN_REFINANCING_OPERATION_RATE = "ECBMRRFR"
# Deposit Facility Rate (Floor) - rate at which clients pay the ECB
ECB_MARGINAL_LENDING_FACILITY_RATE = "ECBMLFR"


def get_stlouisfed_observation(seriesid, interval="monthly", debug=False):
    observation_start = get_past_date_in_yyyy_mm_dd(30 if interval == "daily" else 365)
    frequency = "w" if interval == "weekly" else "d" if interval == "daily" else "m"
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={seriesid}&api_key={API_FRED_KEY}&file_type=json&observation_start={observation_start}&frequency={frequency}&sort_order=desc'
    response = requests.get(url)
    data = response.json()
    observations = data['observations']
    if debug:
        for item in observations:
            logger.info(f"{item['date']} : {item['value']}%")

    latest_rate = None
    # if the data hasn't been updated on the api provider end, it returns a dot instead of numeric value.
    # it is necessary to skip these values if exists.
    offset = 0
    for item in observations:
        if str_can_be_decimal(item['value']):
            latest_rate = Decimal(item['value'])
            break
        else:
            offset += 1
    if latest_rate == None:
        logger.info(f"Could not fetch the current value of ({seriesid}) index!")
        return
    yesterday, last_week, last_month, last_year = None, None, None, None
    daily_delta, weekly_delta, monthly_delta, yearly_delta = None, None, None, None
    if interval == "monthly":
        last_month = get_list_item(observations, offset + 1)
        last_year = get_list_item(observations, offset + 12)
    elif interval == "weekly":
        last_week = get_list_item(observations, offset + 1)
        last_month = get_list_item(observations, offset + 3)
        last_year = get_list_item(observations, offset + 51)
    elif interval == "daily":
        yesterday = get_list_item(observations, offset + 1)
        last_week = get_list_item(observations, offset + 6)
        last_month = get_list_item(observations, offset + 29)
        last_year = get_list_item(observations, offset + 364)
    if yesterday:
        if str_can_be_decimal(yesterday['value']):
            daily_delta = latest_rate - Decimal(yesterday['value'])
    if last_week:
        if str_can_be_decimal(last_week['value']):
            weekly_delta = latest_rate - Decimal(last_week['value'])
    if last_month:
        if str_can_be_decimal(last_month['value']):
            monthly_delta = latest_rate - Decimal(last_month['value'])
    if last_year:
        if str_can_be_decimal(last_year['value']):
            yearly_delta = latest_rate - Decimal(last_year['value'])

    changed = False
    created = False
    try:
        index = EconomicIndex.objects.get(id=seriesid)
        changed = True
        index.value = latest_rate
        index.daily_delta = daily_delta
        index.weekly_delta = weekly_delta
        index.monthly_delta = monthly_delta
        index.yearly_delta = yearly_delta
        index.save()
    except EconomicIndex.DoesNotExist:
        created = True
        kwargs = {'id': seriesid, 'value': latest_rate}
        if daily_delta:
            kwargs['daily_delta'] = daily_delta
        if weekly_delta:
            kwargs['weekly_delta'] = weekly_delta
        if monthly_delta:
            kwargs['monthly_delta'] = monthly_delta
        if yearly_delta:
            kwargs['yearly_delta'] = yearly_delta
        index = EconomicIndex.objects.create(**kwargs)
        index.save()
    if created:
        logger.info(
            f"Successfully created economic index ({seriesid}) : ({latest_rate})%"
        )
    elif changed:
        logger.info(
            f"Successfully updated economic index ({seriesid} : {latest_rate})%"
        )
    else:
        logger.info(
            f"It looks like the index of series id ({seriesid}) hasn't changed."
        )


def get_fed_funds_rate(debug=False):
    get_stlouisfed_observation(FED_FUNDS_RATE_ID, "monthly", debug)


# Floor
def get_ecb_dfr(debug=False):
    get_stlouisfed_observation(ECB_DEPOSIT_FACILITY_RATE, "weekly", debug)


# Average
def get_ecb_mror(debug=False):
    get_stlouisfed_observation(ECB_MAIN_REFINANCING_OPERATION_RATE, "weekly", debug)


# Ceiling
def get_ecb_lfr(debug=False):
    get_stlouisfed_observation(ECB_MARGINAL_LENDING_FACILITY_RATE, "weekly", debug)
