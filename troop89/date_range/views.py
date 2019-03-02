#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Class based views for items that span between two dates.

The hierarchical structure of these views parallels that of the generic date
views shipped with django. These views offer nearly the same interface with a
few notable exceptions:
 - No ``date_list`` context variable is passed along to the template.
 - By default, items are ordered by date ascending rather than date descending.

Only a partial set of the generic date-based views have been adapted for
date-spanning items. Currently, only the following cases are supported:
 - list of date-spanning items by month
 - list of date-spanning items by day
"""

import datetime
import functools

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import Q
from django.shortcuts import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic.base import View
from django.views.generic.dates import (
    BaseDayArchiveView, DateMixin, DayMixin, MonthMixin,
    YearMixin, _date_from_string, timezone_today,
)
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin


class DateRangeMixin(DateMixin):
    """
    Mixin class for views manipulating date-range-based data.
    """
    date_field_start = None
    date_field_end = None

    def get_date_field_start(self):
        """Get the name of the start date field to be used to filter by."""
        if self.date_field_start is None:
            if self.date_field is None:
                raise ImproperlyConfigured(
                    "{0}.date_field_start or {0}.date_field is required.".format(self.__class__.__name__)
                )
            return self.date_field
        return self.date_field_start

    def get_date_field_end(self):
        """Get the name of the end date field to be used to filter by."""
        if self.date_field_end is None:
            raise ImproperlyConfigured("{}.date_field_end is required.".format(self.__class__.__name__))
        return self.date_field_end

    def get_date_field(self):
        return self.get_date_field_start()

    @cached_property
    def uses_datetime_field(self):
        """
        Return `True` if the date field is a `DateTimeField` and `False`
        if it's a `DateField`.
        """
        model = self.get_queryset().model if self.model is None else self.model

        start_field = model._meta.get_field(self.get_date_field_start())
        end_field = model._meta.get_field(self.get_date_field_end())

        start_datetime = isinstance(start_field, models.DateTimeField)
        end_datetime = isinstance(end_field, models.DateTimeField)

        if start_datetime != end_datetime:
            raise ImproperlyConfigured("{0}.end_date_field and {0}.start_date_field MUST be of the same field type.")
        return start_datetime

    def _make_single_date_lookup(self, date):
        """
        Get the lookup kwargs for filtering on a single date.
        """
        start_date_field = self.get_date_field_start()
        end_date_field = self.get_date_field_end()

        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(
            date if not self.uses_datetime_field else date + datetime.timedelta(days=1)
        )

        return {
            '{}__gte'.format(end_date_field): since,
            '{}__lt'.format(start_date_field): until,
        }


class BaseDateRangeListView(MultipleObjectMixin, DateRangeMixin, View):
    """
    Abstract base class for date-range-based views displaying a list of objects.
    """

    def get(self, request, *args, **kwargs):
        # Note that the date_list context variable is omitted.
        self.object_list, extra_context = self.get_items()
        context = self.get_context_data(
            object_list=self.object_list,
            **extra_context
        )
        return self.render_to_response(context)

    def get_items(self):
        """Obtain the list items."""
        raise NotImplementedError('A DateRangeView must provide an implementation of get_items()')

    def get_ordering(self):
        """
        Return the field or fields to use for ordering the queryset; use the
        date fields by default.
        """
        return (
            '{}'.format(self.get_date_field_start(), '{}'.format(self.get_date_field_end()))
        ) if self.ordering is None else self.ordering

    def get_dated_queryset(self, *args, **lookup):
        """
        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        qs = self.get_queryset().filter(*args, **lookup)
        end_field = self.get_date_field_end()
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()
        paginate_by = self.get_paginate_by(qs)

        if not allow_future:
            now = timezone.now() if self.uses_datetime_field else timezone_today()
            qs = qs.filter(**{'%s__lte' % end_field: now})

        if not allow_empty:
            # When pagination is enabled, it's better to do a cheap query
            # than to load the unpaginated queryset in memory.
            is_empty = len(qs) == 0 if paginate_by is None else not qs.exists()
            if is_empty:
                raise Http404("No %(verbose_name_plural)s available".format(
                    verbose_name_plural=qs.model._meta.verbose_name_plural,
                ))

        return qs


class BaseMonthDateRangeView(YearMixin, MonthMixin, BaseDateRangeListView):
    """List of objects that overlap with a given month."""

    def get_items(self):
        """ Return the (object_list, extra_context) for this request."""
        year = self.get_year()
        month = self.get_month()

        date_field_start = self.get_date_field_start()
        date_field_end = self.get_date_field_end()

        date = _date_from_string(year, self.get_year_format(), month, self.get_month_format())

        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_month(date))

        # Query for items that either start or end during the given month
        lookup_args = (Q(**{'{}__gte'.format(df): since}) & Q(**{'{}__lt'.format(df): until})
                       for df in (date_field_start, date_field_end))

        lookup_args = functools.reduce(Q.__or__, lookup_args)

        qs = self.get_dated_queryset(lookup_args)

        return (qs, {
            'month': date,
            'next_month': self.get_next_month(date),
            'previous_month': self.get_previous_month(date),
        })


class MonthDateRangeView(MultipleObjectTemplateResponseMixin, BaseMonthDateRangeView):
    """List of objects that overlap with a given month."""
    template_name_suffix = '_archive_month'


class BaseDayDateRangeView(YearMixin, MonthMixin, DayMixin, BaseDateRangeListView):
    """List of objects that overlap with a given day."""

    get_items = BaseDayArchiveView.get_dated_items

    def _get_dated_items(self, date):
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = self.get_dated_queryset(**lookup_kwargs)

        return (qs, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date),
            'previous_month': self.get_previous_month(date),
            'next_month': self.get_next_month(date)
        })


class DayDateRangeView(MultipleObjectTemplateResponseMixin, BaseDayDateRangeView):
    """List of objects that overlap with a given day."""
    template_name_suffix = "_archive_day"
