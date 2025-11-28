from django.db import models
from auth_system.models import Account
# Create your models here.
class EventType(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    type= models.CharField(max_length=100)
    experience = models.IntegerField()


class Event(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="events")
    event = models.ForeignKey(EventType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.user.add_experience(self.event.exp_reward)