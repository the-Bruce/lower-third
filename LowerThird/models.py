import random
import string

from django.db import models

# Create your models here.
from django.utils import timezone


class Scene(models.Model):
    line1 = models.CharField(max_length=30)
    line2 = models.CharField(max_length=50)

    def __str__(self):
        return self.line1 + ": " + self.line2


class Program(models.Model):
    name = models.CharField(max_length=20)
    scenes = models.ManyToManyField(Scene, through='ProgramScene')

    def __str__(self):
        return self.name


class ProgramScene(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        unique_together = (('program', 'order'),)
        ordering = ('order',)

    def __str__(self):
        return str(self.scene) + ": " + str(self.order)


def new_session():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(5))


class Session(models.Model):
    class States(models.TextChoices):
        INITIALISING = "Init"
        BLANK = "Blank"
        ACTIVE = "Active"

    session = models.CharField(max_length=5, default=new_session, unique=True)
    date = models.DateField(default=timezone.now)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    state = models.CharField(max_length=10, choices=States.choices, default=States.INITIALISING)

    def __str__(self):
        return self.session
