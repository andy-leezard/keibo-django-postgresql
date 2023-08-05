from celery import shared_task
from datetime import datetime
from .api_crypto import get_crypto_prices
from .api_currency import get_exchange_rates

# from celery.exceptions import SoftTimeLimitExceeded

""" 
try:
    do something...
except SoftTimeLimitExceeded:
    clean up proces...
"""

"""soft_time_limit=60, time_limit=70"""


@shared_task()
def print_current_time():
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current time: {current_timestamp}")


@shared_task()
def update_exchange_rate():
    get_exchange_rates()


@shared_task()
def update_crypto_prices():
    get_crypto_prices()
