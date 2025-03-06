
# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localtime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=20)
    last_reset = models.DateField(default=now)

    def reset_credits(self):
        """Resets credits daily at midnight."""
        today = localtime().date()
        if self.last_reset != today:
            self.credits = 20
            self.last_reset = today
            self.save()
            
class CreditRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_credits = models.IntegerField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.requested_credits} credits"
