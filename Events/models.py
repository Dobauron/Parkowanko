from django.db import models
from auth_system.models import Account
# Create your models here.
class EventType(models.Model):
    type= models.CharField(max_length=100)
    experience = models.IntegerField()


class Event(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="events")
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
