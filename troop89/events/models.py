#  Copyright (c) 2018, 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import tzinfo

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


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

    description = MarkdownxField()

    type = models.ForeignKey(EventType, on_delete=models.CASCADE)

    start = models.DateTimeField(default=timezone.now)

    end = models.DateTimeField()

    class Meta:
        ordering = ('start', 'title')

    # todo: revise formatting to be more user friendly
    def __str__(self):
        if self.single_day():
            return '{} ({})'.format(self.title, self.start.ctime())

        return '{} ({} - {})'.format(self.title, self.start.ctime(), self.end.ctime())

    def get_absolute_url(self):
        # Note: we localize the date for display here in order to simplify
        # detail view logic (Django localizes by default). A formal
        # decision regarding EST vs UTC times in urls will need to be
        # made in the future.
        day = timezone.localdate(self.start)
        return reverse('events:event-detail', args=(day.year, day.month, day.day, self.slug))

    @property
    def formatted_description(self):
        """Render this event's markdown description into HTML."""
        return markdownify(self.description)

    def single_day(self) -> bool:
        return self.start.date() == self.end.date()

    def local_date_range(self, timezone: tzinfo = None):
        from .util import local_date_range

        return local_date_range(self.start, self.end, timezone)
