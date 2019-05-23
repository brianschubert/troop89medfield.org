#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.db.models import Prefetch
from django.views.generic import DetailView, dates

from troop89.trooporg.models import Member
from .models import Announcement


class AnnouncementViewMixin:
    model = Announcement

    date_field = 'pub_date'

    context_object_name = 'announcements'

    def get_allow_future(self):
        """Allow users with admin access to view future announcements."""
        return self.request.user.is_staff

    def get_queryset(self):
        prefetch_author = Prefetch(
            'author',
            queryset=Member.objects.all(),
        )
        return super().get_queryset().prefetch_related(prefetch_author)


class AnnouncementIndexView(AnnouncementViewMixin, dates.ArchiveIndexView):
    paginate_by = 5


class AnnouncementYearView(AnnouncementViewMixin, dates.YearArchiveView):
    make_object_list = True
    paginate_by = 5


class AnnouncementMonthView(AnnouncementViewMixin, dates.MonthArchiveView):
    paginate_by = 5


class AnnouncementDetailView(AnnouncementViewMixin, DetailView, dates.BaseDateDetailView):
    context_object_name = 'announcement'
