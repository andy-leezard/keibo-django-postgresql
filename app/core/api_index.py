import requests
import logging
from core.models import EconomicIndex
from keibo.settings import API_FRED_KEY, API_ECOS_BOK_KR_KEY
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

logger = logging.getLogger(__name__)


def get_past_date_in_yyyy_mm_dd(days: int, without_dash=False):
    current_date = datetime.now()
    date_ago = current_date - timedelta(days)
    if without_dash:
        return date_ago.strftime('%Y%m%d')
    return date_ago.strftime('%Y-%m-%d')


def get_past_date_in_yyyy_mm(days: int, without_dash=False):
    current_date = datetime.now()
    date_ago = current_date - timedelta(days)
    if without_dash:
        return date_ago.strftime('%Y%m')
    return date_ago.strftime('%Y-%m')


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

# Inflation
# Euro zone
INFLATION_EURO_ZONE = "FPCPITOTLZGEMU"
# USD USA
INFLATION_USD = "FPCPITOTLZGUSA"
# KRW Korea
INFLATION_KRW = "FPCPITOTLZGKOR"
# Yuan China
INFLATION_YUAN = "FPCPITOTLZGCHN"
# Yen Japan
INFLATION_YEN = "FPCPITOTLZGJPN"
# Ruble Russia
INFLATION_RUBLE = "FPCPITOTLZGRUS"
# GBP UK
INFLATION_GBP = "FPCPITOTLZGGBR"
# Rupiah Indonesia
INFLATION_IDR = "FPCPITOTLZGIDN"
# Rupee India
INFLATION_RUPEE = "FPCPITOTLZGIND"
# AED (United Arab Emirates Dirham)
INFLATION_AED = "FPCPITOTLZGARE"
# Switzerland Franc
INFLATION_CHF = "FPCPITOTLZGCHE"


def get_stlouisfed_observation(seriesid, interval="monthly", debug=False):
    observation_start = get_past_date_in_yyyy_mm_dd(
        3650 if interval == "annual" else 30 if interval == "daily" else 365
    )
    frequency = (
        "a"
        if interval == "annual"
        else "w"
        if interval == "weekly"
        else "d"
        if interval == "daily"
        else "m"
    )
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
    yesterday, last_week, last_month, last_year, last_decade = (
        None,
        None,
        None,
        None,
        None,
    )
    daily_delta, weekly_delta, monthly_delta, yearly_delta, decennial_delta = (
        None,
        None,
        None,
        None,
        None,
    )
    if interval == "annual":
        last_year = get_list_item(observations, offset + 1)
        last_decade = get_list_item(observations, offset + 9)
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
    if last_decade:
        if str_can_be_decimal(last_decade['value']):
            decennial_delta = latest_rate - Decimal(last_decade['value'])

    created = False
    try:
        index = EconomicIndex.objects.get(id=seriesid)
        index.value = latest_rate
        index.daily_delta = daily_delta
        index.weekly_delta = weekly_delta
        index.monthly_delta = monthly_delta
        index.yearly_delta = yearly_delta
        index.decennial_delta = decennial_delta
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
        if decennial_delta:
            kwargs['decennial_delta'] = decennial_delta
        index = EconomicIndex.objects.create(**kwargs)
    if created:
        logger.info(
            f"Successfully created economic index ({seriesid}) : ({latest_rate})%"
        )
    else:
        logger.info(
            f"Successfully updated economic index ({seriesid} : {latest_rate})%"
        )


def get_ecos_bok_kr(asset_class, debug=False):
    year_ago = get_past_date_in_yyyy_mm(365, True)
    today = get_past_date_in_yyyy_mm(0, True)
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{API_ECOS_BOK_KR_KEY}/json/kr/1/12/{asset_class}/M/{year_ago}/{today}'
    response = requests.get(url)
    result = response.json()
    rows: List = result['StatisticSearch']['row']
    rows.reverse()
    if debug:
        for row in rows:
            logger.info(f"{row['TIME']} : {row['DATA_VALUE']}")
    latest_rate = get_list_item(rows, 0)
    last_month = get_list_item(rows, 1)
    last_year = get_list_item(rows, 11)
    monthly_delta, yearly_delta = None, None
    if latest_rate == None or not str_can_be_decimal(latest_rate['DATA_VALUE']):
        logger.info(
            f"get_ecos_bok_kr - failed to get the latest_rate for {asset_class}%"
        )
        return
    latest_rate = Decimal(latest_rate['DATA_VALUE'])
    if last_month:
        if str_can_be_decimal(last_month['DATA_VALUE']):
            monthly_delta = latest_rate - Decimal(last_month['DATA_VALUE'])
    if last_year:
        if str_can_be_decimal(last_year['DATA_VALUE']):
            yearly_delta = latest_rate - Decimal(last_year['DATA_VALUE'])
    created = False
    try:
        index = EconomicIndex.objects.get(id=asset_class)
        index.value = latest_rate
        index.monthly_delta = monthly_delta
        index.yearly_delta = yearly_delta
        index.save()
    except EconomicIndex.DoesNotExist:
        created = True
        EconomicIndex.objects.create(
            id=asset_class,
            value=latest_rate,
            monthly_delta=monthly_delta,
            yearly_delta=yearly_delta,
        )
    if created:
        logger.info(
            f"Successfully created economic index ({asset_class}) : ({latest_rate})%"
        )
    else:
        logger.info(
            f"Successfully updated economic index ({asset_class} : {latest_rate})%"
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


def get_bok_interest_rates(debug=False):
    get_ecos_bok_kr('722Y001', debug)


def get_inflation_euro(debug=False):
    get_stlouisfed_observation(INFLATION_EURO_ZONE, "annual", debug)


def get_inflation_usd(debug=False):
    get_stlouisfed_observation(INFLATION_USD, "annual", debug)


def get_inflation_krw(debug=False):
    get_stlouisfed_observation(INFLATION_KRW, "annual", debug)


def get_inflation_yuan(debug=False):
    get_stlouisfed_observation(INFLATION_YUAN, "annual", debug)


def get_inlfation_yen(debug=False):
    get_stlouisfed_observation(INFLATION_YEN, "annual", debug)


def get_inflation_ruble(debug=False):
    get_stlouisfed_observation(INFLATION_RUBLE, "annual", debug)


def get_inflation_gbp(debug=False):
    get_stlouisfed_observation(INFLATION_GBP, "annual", debug)


def get_inflation_idr(debug=False):
    get_stlouisfed_observation(INFLATION_IDR, "annual", debug)


def get_inflation_rupee(debug=False):
    get_stlouisfed_observation(INFLATION_RUPEE, "annual", debug)


def get_inflation_aed(debug=False):
    get_stlouisfed_observation(INFLATION_AED, "annual", debug)


def get_inflation_chf(debug=False):
    get_stlouisfed_observation(INFLATION_CHF, "annual", debug)

def get_all_index(debug=False):
    get_fed_funds_rate(debug)
    get_ecb_dfr(debug)
    get_ecb_mror(debug)
    get_ecb_lfr(debug)
    get_bok_interest_rates(debug)
    get_inflation_euro(debug)
    get_inflation_usd(debug)
    get_inflation_krw(debug)
    get_inflation_yuan(debug)
    get_inlfation_yen(debug)
    get_inflation_ruble(debug)
    get_inflation_gbp(debug)
    get_inflation_idr(debug)
    get_inflation_rupee(debug)
    get_inflation_aed(debug)
    get_inflation_chf(debug)