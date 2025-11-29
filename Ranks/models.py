from django.db import models

# Create your models here.
class Rank(models.Model):
    name = models.CharField(max_length=255, blank=True)
    required_exp = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["required_exp"]

    def __str__(self):
        return self.name

class UserRank(models.Model):
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)
    current_exp = models.PositiveIntegerField(default=0)