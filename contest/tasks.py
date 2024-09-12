from celery import shared_task
from .models import Contest
from django.utils.timezone import now

@shared_task(bind=True)
def update_contest_status(self):
    current_time = now()
    contests = Contest.objects.all()

    for contest in contests:
        print('celery is changes status of contest')
        if contest.start_time <= current_time <= contest.end_time:
            contest.status = 'ongoing'
        elif current_time > contest.end_time:
            contest.status = 'finished'
        else:
            contest.status = 'scheduled'

        contest.save()


@shared_task
def test_task():
    print("Test task is running")
    return "Task completed"