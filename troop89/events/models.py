from datetime import tzinfo

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


class EventType(models.Model):
    label = models.CharField(max_length=28, blank=False)

    def __str__(self):
        return self.label


class Event(models.Model):
    title = models.CharField(max_length=36, blank=False)

    slug = models.SlugField(
        unique_for_date="start",
        help_text="URL Slug that identifies this event. "
                  "Changing this will invalidate existing urls pointing to this event."
    )

    description = models.TextField()

    type = models.ForeignKey(EventType, on_delete=models.CASCADE)

    start = models.DateTimeField(default=timezone.now)

    end = models.DateTimeField()

    # todo: revise formatting to be more user friendly
    def __str__(self):
        if self.single_day():
            return '{} ({})'.format(self.title, self.start.ctime())

        return '{} ({} - {})'.format(self.title, self.start.ctime(), self.end.ctime())

    def get_absolute_url(self):
        day = self.start
        return reverse('events:event-detail', args=(day.year, day.month, day.day, self.slug))

    def single_day(self) -> bool:
        return self.start.date() == self.end.date()

    def local_date_range(self, timezone: tzinfo = None):
        from .util import local_date_range

        return local_date_range(self.start, self.end, timezone)
