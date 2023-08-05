import requests
import logging
from decimal import Decimal
from core.models import Asset, AssetCategory
from keibo.settings import (
    API_PROVIDER_KEY_HEADER,
    API_PROVIDER_HOST_HEADER,
    API_PROVIDER_KEY,
    API_EXCHANGE_RATES_HOST,
    API_EXCHANGE_RATES,
)

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = {
    'usd',
    'eur',
    'chf',
    'gbp',
    'jpy',
    'rub',
    'krw',
    'cny',
    'cad',
    'inr',
}


def get_exchange_rates():
    url = API_EXCHANGE_RATES

    headers = {
        API_PROVIDER_KEY_HEADER: API_PROVIDER_KEY,
        API_PROVIDER_HOST_HEADER: API_EXCHANGE_RATES_HOST,
    }

    try:
        response = requests.get(url, headers=headers)  # type: ignore

        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as e:
        logger.info(f"Request to {url} failed with exception: {e}")
        return

    data = response.json()
    rates = data.get('rates')

    if not isinstance(rates, dict):
        logger.info("Unexpected data format. 'rates' should be a dictionary.")
        return

    for currency, rate in rates.items():
        if not isinstance(currency, str):
            logger.info(
                f"Unexpected currency type. Currencies should be strings, but got {type(currency)}."
            )
            return
        if not isinstance(
            rate, (int, float, Decimal)
        ):  # Accept any kind of number, for flexibility
            logger.info(
                f"Unexpected rate type. Rates should be numbers, but got {type(rate)}."
            )
            return

    new_assets = 0
    updated_assets = 0
    for currency, rate in rates.items():
        currency = currency.lower()
        # Register only supported currencies
        if currency in SUPPORTED_CURRENCIES:
            try:
                asset = Asset.objects.get(id=currency)
                asset.exchange_rate = rate
                asset.save()
                updated_assets += 1
            except Asset.DoesNotExist:
                new_assets += 1
                Asset.objects.create(
                    id=currency, exchange_rate=rate, category=AssetCategory.CASH
                )

    logger.info(f"Currencies: added {new_assets} and updated {updated_assets} assets!")
