from celery import shared_task
from datetime import datetime


@shared_task
def my_scheduled_task():
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"This task is run every hour. Current time: {current_timestamp}")
