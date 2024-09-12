from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_periodic_task(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    from django.db.utils import OperationalError, ProgrammingError

    try:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1, 
            period=IntervalSchedule.MINUTES,
        )
        
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Update Contest Status',
            task='contest.tasks.update_contest_status',
        )
    except (OperationalError, ProgrammingError):
        # Database isn't ready yet, pass silently.
        pass

class ContestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contest'

    def ready(self):
        post_migrate.connect(create_periodic_task, sender=self)