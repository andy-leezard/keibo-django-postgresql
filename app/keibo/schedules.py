from datetime import timedelta

# Currently disabled to use django-celery-beat interface instead.

my_scheduled_task = {
    'task': 'core.tasks.update_exchange_rate',
    'schedule': timedelta(hours=4),
}
