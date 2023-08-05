import requests
import logging
from core.models import EconomicIndex
from keibo.settings import API_FRED_KEY

logger = logging.getLogger(__name__)

# Primary key
FED_FUNDS_RATE_ID = "fed_funds_rate"


def get_fed_funds_rate():
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={API_FRED_KEY}&file_type=json'
    response = requests.get(url)
    data = response.json()

    # Get the latest available rate
    latest_rate = data['observations'][-1]['value']
    last_month_rate = data['observations'][-2]['value']
    last_year_rate = data['observations'][-13]['value']

    monthly_delta = latest_rate - last_month_rate
    yearly_delta = latest_rate - last_year_rate
    changed = False
    created = False
    try:
        asset = EconomicIndex.objects.get(id=FED_FUNDS_RATE_ID)
        if asset.value != latest_rate:
            changed = True
            asset.value = latest_rate
            asset.monthly_delta = monthly_delta
            asset.yearly_delta = yearly_delta
    except EconomicIndex.DoesNotExist:
        created = True
        EconomicIndex.objects.create(
            id=FED_FUNDS_RATE_ID,
            value=latest_rate,
            monthly_delta=monthly_delta,
            yearly_delta=yearly_delta,
        )
    if created:
        logger.info(f"Successfully created the fed funds rate index ({latest_rate})%")
    elif changed:
        logger.info(f"Successfully created the fed funds rate index ({latest_rate})%")
    else:
        logger.info(f"It looks like the fed funds rate hasn't changed.")
