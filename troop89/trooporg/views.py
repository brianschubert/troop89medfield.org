#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from typing import List, Optional, Tuple

from django.db.models import Prefetch
from django.shortcuts import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin

from .models import Patrol, PatrolMembership, PositionInstance, Term


class PatrolArchiveView(ListView):
    model = Patrol


class PatrolDetailView(DetailView):
    model = Patrol

    def get_queryset(self):
        prefetch_memberships = Prefetch(
            'memberships',
            queryset=PatrolMembership.objects
                .select_related('scout', 'term')
                .order_by('-term__start', 'type')
        )
        return super().get_queryset().prefetch_related(prefetch_memberships)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # All memberships will be looped over in the template so its OK to
        # resolve the query set now.
        # Normally, the below filtering SHOULD be performed at the database level.
        # However, since all the memberships for this patrol have already been
        # fetched - along with their related fields - filtering in python was
        # assumed to be more efficient.
        current_memberships = [m for m in self.object.memberships.all() if m.term.is_current()]
        if current_memberships:
            context['current_memberships'] = current_memberships
            context['current_term'] = current_memberships[0].term
        return context


class BaseTermDetailView(DetailView):
    model = Term

    def get_date(self) -> datetime.date:
        """Return the date for which this view should display a Term."""
        raise NotImplemented("A TermDetailView must provide an implementation of get_date()")

    def get_object(self, queryset=None) -> Optional[Term]:
        self.date = self.get_date()

        if queryset is None:
            queryset = self.get_queryset()

        # A plethora of prefetches to prevent a plethora of queries
        prefetch_positions = Prefetch(
            'position_instances',
            # List youth positions first
            queryset=PositionInstance.objects
                .add_grouping_name()
                .select_related('incumbent')
                .order_by('type__is_adult', '-type__is_leader', '-type__precedence')
        )
        prefetch_memberships = Prefetch(
            'patrol_memberships',
            # Sort memberships by (patrol,type) for regroup tags
            queryset=PatrolMembership
                .objects
                .select_related('scout', 'patrol')
                .order_by('patrol__name', 'type')
        )
        queryset = queryset \
            .prefetch_related(prefetch_positions) \
            .prefetch_related(prefetch_memberships)

        try:
            return queryset.get(start__lte=self.date, end__gt=self.date)
        except Term.DoesNotExist:
            return None  # todo: consider whether raising an Http404 would be more appropriate

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top, bottom = self._partitioned_position_instances()
        context['top_positions'] = top
        context['bottom_positions'] = bottom
        context['date'] = self.date

        return context

    def _partitioned_position_instances(self) -> Tuple[List[PositionInstance], List[PositionInstance]]:
        """Split this term's positions into two logical groups."""
        top_positions, bottom_positions = [], []
        if self.object:
            for position in self.object.position_instances.all():
                # Assume that type has been pre-selected
                if not position.type.is_adult and position.type.is_leader:
                    top_positions.append(position)
                else:
                    bottom_positions.append(position)
        return top_positions, bottom_positions


class TermDetailView(YearMixin, MonthMixin, DayMixin, BaseTermDetailView):
    """Term that contains the given date."""

    def get_date(self) -> datetime.date:
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        try:
            return datetime.date(year, month, day)
        except ValueError as e:
            raise Http404(f'No such date: {year}-{month}-{day} ({str(e)})')


class CurrentTermDetailView(BaseTermDetailView):
    """Term that contains today."""

    def get_date(self) -> datetime.date:
        return datetime.date.today()


class TermListView(ListView):
    model = Term
