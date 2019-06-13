#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import calendar

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from troop89.trooporg.models import Member


class AnnouncementQuerySet(models.QuerySet):
    """Query set for announcement instances."""

    def published(self):
        return self.filter(pub_date__lte=timezone.now())


class Announcement(models.Model):
    """An announcement posted on the site's main page."""
    title = models.CharField(max_length=120, blank=False)

    slug = models.SlugField(
        unique_for_date='pub_date',
        help_text="URL Slug that identifies this announcement. "
                  "Changing this will invalidate existing urls pointing to this announcement.",
    )

    pub_date = models.DateTimeField(default=timezone.now, verbose_name="Date of Publication")

    content = MarkdownxField(verbose_name='Post Content')

    author = models.ForeignKey(Member, on_delete=models.PROTECT)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __str__(self):
        return f'{self.title} ({self.pub_date.date()})'

    def get_absolute_url(self):
        day = timezone.localdate(self.pub_date)
        return reverse('announcements:announcement-detail', args=(day.year, day.month, day.day, self.slug))

    @cached_property
    def formatted_content(self):
        """Render this announcement markdown content into HTML."""
        return markdownify(self.content)

    @property
    def breadcrumbs(self):
        """Return this announcement's breadcrumb trail."""
        local_date = timezone.localdate(self.pub_date)
        return [
            (
                "Announcements",
                reverse('announcements:announcement-index')
            ),
            (
                str(local_date.year),

                reverse('announcements:announcement-archive-year', args=(local_date.year,)),
            ),
            (
                calendar.month_name[local_date.month],
                reverse('announcements:announcement-archive-month', args=(local_date.year, local_date.month), ),
            ),
            (
                self.title,
                reverse('announcements:announcement-detail',args=(local_date.year, local_date.month, local_date.day, self.slug),)
            ),
        ]
