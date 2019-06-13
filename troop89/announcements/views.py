#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import calendar

from django.db.models import Prefetch
from django.urls import reverse
from django.views.generic import DetailView, View, dates

from troop89.json_ld.views import BreadcrumbJsonLdMixin
from troop89.trooporg.models import Member
from .models import Announcement


class AnnouncementViewMixin(BreadcrumbJsonLdMixin):
    model = Announcement

    date_field = 'pub_date'

    context_object_name = 'announcements'

    def __init__(self, **kwargs):
        # See comment in troop89.events.views.EventBreadcrumbMixin.__init__()
        View.__init__(self, **kwargs)
        super().__init__()

    def get_allow_future(self):
        """Allow users with admin access to view future announcements."""
        return self.request.user.is_staff

    def get_queryset(self):
        prefetch_author = Prefetch(
            'author',
            queryset=Member.objects.all(),
        )
        return super().get_queryset().prefetch_related(prefetch_author)

    def get_breadcrumbs(self):
        return [("Announcements", reverse('announcements:announcement-index'))]


class AnnouncementIndexView(AnnouncementViewMixin, dates.ArchiveIndexView):
    paginate_by = 5


class AnnouncementYearView(AnnouncementViewMixin, dates.YearArchiveView):
    make_object_list = True
    paginate_by = 5

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        year = self.get_year()
        breadcrumbs.append((
            str(year),
            reverse("announcements:announcement-archive-year", args=(year,))
        ))
        return breadcrumbs


class AnnouncementMonthView(AnnouncementViewMixin, dates.MonthArchiveView):
    paginate_by = 5

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        year = self.get_year()
        month = self.get_month()
        breadcrumbs += [
            (
                str(year),
                reverse("announcements:announcement-archive-year", args=(year,)),
            ),
            (
                calendar.month_name[month],
                reverse("announcements:announcement-archive-month", args=(year, month))
            ),
        ]
        return breadcrumbs


class AnnouncementDetailView(AnnouncementViewMixin, DetailView, dates.BaseDateDetailView):
    context_object_name = 'announcement'

    def get_breadcrumbs(self):
        return self.object.breadcrumbs
