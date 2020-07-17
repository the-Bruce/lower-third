import datetime
import io
import random
import string

from PIL import Image

from django.db import models
from django.contrib.auth import models as users
from django.core.files import File
import logging
import matplotlib
import matplotlib.dates
import matplotlib.axis
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

logger = logging.getLogger("co.uk.thomasbruce.ely.count")

# Create your models here.
from django.urls import reverse
from django.utils import timezone

locator = mdates.HourLocator()
formatter = mdates.DateFormatter("%H:%M")


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


class Graph(models.Model):
    date = models.ForeignKey(DayCount, on_delete=models.CASCADE)
    graph = models.ImageField(blank=True, editable=False, upload_to='graphs/')

    @property
    def graph_safe(self):
        if self.graph == "":
            self._gengraph()
        return self.graph

    @staticmethod
    def _get_random_string(length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def _gengraph(self):
        logger.info("Generating: "+str(self.date.date))
        day = matplotlib.dates.date2num(self.date.date)
        start = matplotlib.dates.date2num(datetime.datetime.combine(self.date.date, datetime.time(hour=9)))
        end = matplotlib.dates.date2num(datetime.datetime.combine(self.date.date, datetime.time(hour=17)))

        deltas = LogItem.objects.filter(time__day=self.date.date.day, time__month=self.date.date.month,
                                        time__year=self.date.date.year).order_by('time')
        dates = []
        values = []

        if len(deltas) == 0:
            dates.append(start)
            values.append(0)
            dates.append(end)
            values.append(0)
        else:
            sum_ = 0
            for i in deltas:
                sum_ += i.delta
                sum_ = max(0, sum_)
                dates.append(matplotlib.dates.date2num(i.time))
                values.append(sum_)

            if dates[0] >= start:
                dates.insert(0, start)
            else:
                dates.insert(0, max(day, matplotlib.dates.date2num(
                    matplotlib.dates.num2date(dates[0]) - datetime.timedelta(hours=1))))
            values.insert(0, 0)

            if dates[-1] <= end:
                dates.append(end)
            else:
                dates.append(min(day + 1, matplotlib.dates.date2num(
                    matplotlib.dates.num2date(dates[-1]) + datetime.timedelta(hours=1))))
            values.append(0)

        fig, ax = plt.subplots(figsize=(20,5))
        fig.autofmt_xdate()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.step(dates, values, where='post')
        with io.BytesIO() as buf:
            fig.savefig(buf, format='png')
            buf.seek(0)

            self.graph.save(str(self.date.date) + '_' + self._get_random_string(4) + '.png', File(buf))

    def get_absolute_url(self):
        return reverse('count:graph',
                       kwargs={"year": self.date.date.year, "month": self.date.date.month, "day": self.date.date.day})

    def __str__(self):
        return str(self.date)
