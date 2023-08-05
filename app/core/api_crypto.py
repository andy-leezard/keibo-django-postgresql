import requests
import logging
from core.models import Asset, AssetCategory
from keibo.settings import (
    API_PROVIDER_KEY_HEADER,
    API_PROVIDER_HOST_HEADER,
    API_PROVIDER_KEY,
    API_CRYPTO_PRICES_HOST,
    API_CRYPTO_PRICES,
)

logger = logging.getLogger(__name__)

SUPPORTED_CRYPTOS = {
    'bitcoin',
    'ethereum',
    'bitcoin-cash',
    'binancecoin',
    'ripple',
    'cardano',
    'solana',
    'tron',
    'dogecoin',
}


def get_crypto_prices():
    url = API_CRYPTO_PRICES

    querystring = {
        "ids": ",".join(SUPPORTED_CRYPTOS),
        "vs_currencies": "usd",
    }

    headers = {
        API_PROVIDER_KEY_HEADER: API_PROVIDER_KEY,
        API_PROVIDER_HOST_HEADER: API_CRYPTO_PRICES_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)  # type: ignore
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as e:
        logger.info(f"Request to {url} failed with exception: {e}")
        return

    crypto_data = response.json()

    new_assets = 0
    updated_assets = 0
    for crypto, details in crypto_data.items():
        rate = details.get('usd')
        if rate is not None:
            crypto = crypto.lower()
            try:
                asset = Asset.objects.get(id=crypto)
                asset.exchange_rate = rate
                asset.save()
                updated_assets += 1
            except Asset.DoesNotExist:
                new_assets += 1
                Asset.objects.create(
                    id=crypto, exchange_rate=rate, category=AssetCategory.CRYPTO
                )

    logger.info(f"Crypto: added {new_assets} and updated {updated_assets} assets!")
