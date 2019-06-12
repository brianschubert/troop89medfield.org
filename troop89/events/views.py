#  Copyright (c) 2018, 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime, now
from django.views import generic
from django_json_ld.views import JsonLdContextMixin

from troop89.date_range.views import DayDateRangeView, MonthDateRangeView
from .models import Event
from .util import EventCalendar


class EventBreadcrumbJsonLdContextMixin(JsonLdContextMixin):
    """
    Mixin for Event views to set structured data in a view's context.

    The ``JsonLdContextMixin`` can not be used to handle the Event views'
    structured data since it's ``__init__`` method does not expect any kwargs,
    but we need to set ``self.month_format`` via a kwarg.

    This mixin resolves this issue by explicitly calling ``View.__init__()``
    before ``super().__init__()``, which presumptively converts all kwargs into
    attributes, removing the need to pass the kwargs to parent ``__init__()``s.

    See `google's page on breadcrumb structured data`_ for more information
    regarding json-ld structured data.

    .. _google's page on breadcrumb structured data: https://developers.google.com/search/docs/data-types/breadcrumb
    """
    structured_data = {
        "@type": 'BreadcrumbList',
    }

    def __init__(self, **kwargs):
        generic.View.__init__(self, **kwargs)
        super().__init__()

    def _make_breadcrumbs_for_date(self, date: datetime):
        return [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Calendar",
                "item": self.request.build_absolute_uri(
                    reverse('events:calendar-month', args=(date.year, date.month))
                )
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": date.strftime("%B %Y Events"),
                "item": self.request.build_absolute_uri(
                    reverse('events:event-archive-month', args=(date.year, date.month))
                )
            },
        ]


class EventMonthView(EventBreadcrumbJsonLdContextMixin, MonthDateRangeView):
    model = Event
    allow_empty = True
    allow_future = True
    date_field_start = 'start'
    date_field_end = 'end'
    context_object_name = 'events'

    def get_structured_data(self):
        """Return this month's structured data for search engine indexing."""
        structured_data = super().get_structured_data()

        date = datetime(self.get_year(), self.get_month(), 1)

        structured_data['itemListElement'] = self._make_breadcrumbs_for_date(date)
        return structured_data


class CalendarMonthView(EventMonthView):
    template_name = 'events/calendar_month.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        year = self.get_year()
        month = self.get_month()
        if object_list is None:
            object_list = []

        calendar = EventCalendar(year, month, object_list)
        context = super().get_context_data(**kwargs)
        context['calendar'] = calendar

        return context

    def get_structured_data(self):
        """Return this calendar's structured data for search engine indexing."""
        structured_data = super().get_structured_data()

        date = datetime(self.get_year(), self.get_month(), 1)
        structured_data['itemListElement'][-1] = {
            "@type": "ListItem",
            "position": 2,
            "name": date.strftime("%B %Y Calendar"),
            "item": self.request.build_absolute_uri(
                reverse('events:calendar-month', args=(date.year, date.month))
            )
        }
        return structured_data


class EventDayView(EventBreadcrumbJsonLdContextMixin, DayDateRangeView):
    model = Event
    allow_empty = True
    allow_future = True
    date_field_start = 'start'
    date_field_end = 'end'
    context_object_name = 'events'

    def get_structured_data(self):
        """Return this day's structured data for search engine indexing."""
        structured_data = super().get_structured_data()

        date = datetime(self.get_year(), self.get_month(), self.get_day())

        item_list = self._make_breadcrumbs_for_date(date)
        item_list.append({
            "@type": "ListItem",
            "position": 3,
            "name": date.strftime("%a %B %d"),
            "item": self.request.build_absolute_uri(
                reverse('events:event-archive-day', args=(date.year, date.month, date.day))
            )
        })
        structured_data['itemListElement'] = item_list
        return structured_data


class EventDetailView(EventBreadcrumbJsonLdContextMixin, generic.DetailView, generic.dates.BaseDateDetailView):
    model = Event
    date_field = 'start'
    allow_future = True

    def get_structured_data(self):
        """Return this event's structured data for search engine indexing."""
        structured_data = super().get_structured_data()

        date = timezone.localdate(self.object.start)

        item_list = self._make_breadcrumbs_for_date(date)
        item_list.extend([
            {
                "@type": "ListItem",
                "position": 3,
                "name": date.strftime("%a %B %d"),
                "item": self.request.build_absolute_uri(
                    reverse('events:event-archive-day', args=(date.year, date.month, date.day))
                )
            },
            {
                "@type": "ListItem",
                "position": 4,
                "name": self.object.title,
                "item": self.request.build_absolute_uri(
                    reverse('events:event-detail', args=(date.year, date.month, date.day, self.object.slug))
                )
            },
        ])
        structured_data['itemListElement'] = item_list
        return structured_data


class RedirectCurrentMonth(generic.RedirectView):
    permanent = False
    pattern_name = "events:calendar-month"

    def get_redirect_url(self, *args, **kwargs):
        today = localtime(now()).date()
        return super().get_redirect_url(year=today.year, month=today.month)
