from django.db import models

# Create your models here.
from django.utils import timezone


class DayCount(models.Model):
    date = models.DateField(default=timezone.now)
    current = models.PositiveSmallIntegerField(default=0)
    peak = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.date)