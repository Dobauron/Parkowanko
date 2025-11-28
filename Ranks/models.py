from django.db import models

# Create your models here.
class Rank(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=50
    )  # np. "nowicjusz", "wojownik"

    name = models.CharField(max_length=255, blank=True)
    required_exp = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["required_exp"]

    def __str__(self):
        return self.id
