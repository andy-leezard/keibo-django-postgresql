from datetime import timedelta

my_scheduled_task = {
    'task': 'core.tasks.my_scheduled_task',
    'schedule': timedelta(hours=1),
}