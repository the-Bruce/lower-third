from django.db import models
from django.contrib.auth import models as users

# Create your models here.
from django.utils import timezone


class DayCount(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    current = models.PositiveSmallIntegerField(default=0)
    peak = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.date)


class LogItem(models.Model):
    userID = models.ForeignKey(users.User, on_delete=models.SET_NULL, blank=True, null=True)
    deviceID = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    delta = models.SmallIntegerField(default=0)
