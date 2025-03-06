# from django_cron import CronJobBase, Schedule
# from .models import Profile
# from django.utils.timezone import localtime

# class ResetCreditsCronJob(CronJobBase):
#     RUN_EVERY_MINS = 1440  # 24 hours

#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = "user.reset_credits"

#     def do(self):
#         today = localtime().date()
#         Profile.objects.filter(last_reset__lt=today).update(credits=20, last_reset=today)
# your_app/cron.py
from django.utils import timezone
from .models import Profile

def reset_credits():
    today = timezone.localdate()
    # Reset credits for all profiles that haven't been updated today
    profiles = Profile.objects.filter(last_reset__lt=today)
    for profile in profiles:
        profile.credits = 20
        profile.last_reset = today
        profile.save()
    print(f"Reset credits for {profiles.count()} profiles")
