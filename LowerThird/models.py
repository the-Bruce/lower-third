import random
import string
from operator import itemgetter

from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone


class Program(models.Model):
    name = models.CharField(max_length=20)
    archived = models.BooleanField(default=False,
                                   help_text="Archived programs don't appear in the selection list for new sessions")

    def __str__(self):
        return self.name


class Scene(models.Model):
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(max_length=80, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="scenes")
    order = models.IntegerField()

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.line1 + ": " + self.line2


def new_session():
    letters = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789"  # Unambiguous letters/numbers
    return ''.join(random.choice(letters) for i in range(5))


def new_key():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(128))


class Session(models.Model):
    class States:
        INITIALISING = "Init"
        BLANK = "Blank"
        ACTIVE = "Active"
        choices = (INITIALISING, "Initialising"), (BLANK, "Blank"), (ACTIVE, "Active")

        def __contains__(self, item):
            return item in map(itemgetter(0), self.choices)

        def __len__(self):
            len(self.choices)

    session = models.CharField(max_length=5, default=new_session, unique=True)
    key = models.CharField(max_length=128, default="", blank=True)
    date = models.DateField(default=timezone.now)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    state = models.CharField(max_length=10, choices=States.choices, default=States.INITIALISING)
    persistent = models.BooleanField(default=False)

    def __str__(self):
        return self.session

    def set_program(self, program):
        self.program = program
        if len(program.scenes.all()) > 0:
            self.scene = program.scenes.first()
        self.state = self.States.BLANK
        self.save()

    def get_absolute_url(self):
        return reverse('lower_third:control', kwargs={'session': self.session})
