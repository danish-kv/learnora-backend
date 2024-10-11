from celery import shared_task
from .models import Contest
from django.utils.timezone import now
from django.core.cache import cache


@shared_task
def update_contest_status_task():
    current_time = now()

    # Fetch relevant contests based on their start and end times
    contests = Contest.objects.all().exclude(status='finished')

    for contest in contests:
        updated_status = None

        if contest.start_time <= current_time <= contest.end_time:
            if contest.status != 'ongoing':
                updated_status = 'ongoing'
        elif current_time > contest.end_time:
            if contest.status != 'finished':
                updated_status = 'finished'
        else:  # current_time < contest.start_time
            if contest.status != 'scheduled':
                updated_status = 'scheduled'

        # Update contest status if it has changed
        if updated_status:
            contest.status = updated_status
            contest.save()

    # Clear the cache only once after processing all contests
    cache.clear()
