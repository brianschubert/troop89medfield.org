import datetime
from typing import Optional

from django.db.models import Prefetch
from django.shortcuts import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin

from .models import Patrol, PatrolMembership, Term


class PatrolArchiveView(ListView):
    model = Patrol


class PatrolDetailView(DetailView):
    model = Patrol

    def get_queryset(self):
        prefetch_memberships = Prefetch(
            'memberships',
            queryset=PatrolMembership.objects.order_by('-term__start', 'type').all()
        )
        return (
            super().get_queryset()
                .prefetch_related(prefetch_memberships)
                .prefetch_related('memberships__scout')
                .prefetch_related('memberships__term')
        )

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

        prefetch_memberships = Prefetch(
            'patrol_memberships',
            queryset=PatrolMembership.objects.order_by('patrol__name', 'type')
        )
        queryset = queryset \
            .prefetch_related(prefetch_memberships) \
            .prefetch_related('patrol_memberships__scout') \
            .prefetch_related('patrol_memberships__patrol')

        try:
            return queryset.get(start__lte=self.date, end__gt=self.date)
        except Term.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.date
        return context


class TermDetailView(YearMixin, MonthMixin, DayMixin, BaseTermDetailView):
    """Term that contains the given date."""

    def get_date(self) -> datetime.date:
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        try:
            return datetime.date(year, month, day)
        except ValueError as e:
            raise Http404('No such date: {year}-{month}-{day} ({reason})'.format(
                year=year,
                month=month,
                day=day,
                reason=str(e),
            ))


class CurrentTermDetailView(BaseTermDetailView):
    """Term that contains today."""

    def get_date(self) -> datetime.date:
        return datetime.date.today()
