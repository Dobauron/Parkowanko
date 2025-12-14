from django.db import models
from auth_system.models import Account


# Create your models here.
class Rank(models.Model):
    name = models.CharField(max_length=255, blank=True)
    required_exp = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["required_exp"]

    def __str__(self):
        return self.name
