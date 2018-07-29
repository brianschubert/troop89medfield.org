import datetime

from django.utils.timezone import now
from django.views import generic

from .models import Event
from .util import EventCalendar


class CalendarMonthView(generic.MonthArchiveView):
    model = Event
    allow_empty = True
    allow_future = True
    template_name = 'events/calendar_month.html'
    date_field = 'start'

    def get_dated_queryset(self, **lookup):
        """
        Intercept the default query arguments to include events that started
        in the previous month.

        NOTE: If memory overhead from fetching events for two months on every
        request becomes an issue, BaseMonthArchiveView.get_dated_items could
        be overridden instead to explicitly fetch only events who will begin
        before or during this month AND who will end in this month.
        """
        date_field = self.get_date_field()
        key = date_field + '__gte'

        lookup[key] = self.get_previous_month(lookup[key])
        return super().get_dated_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        year = self.get_year()
        month = self.get_month()
        if object_list is None:
            object_list = []

        calendar = EventCalendar(year, month, object_list)
        context = super().get_context_data(**kwargs)
        context['calendar'] = calendar

        return context


class EventDayView(generic.DayArchiveView):
    model = Event
    allow_empty = True
    allow_future = True
    date_field = 'start'
    context_object_name = 'events'

    def _make_single_date_lookup(self, date):
        """
        Get the lookup kwargs for filtering on a single date.

        Event's are relevant for all days that they overlap with, not just the
        day that they start on. By default, only the start field would be
        examined when querying for events by date. We need all events whose
        start time is less than the current date and whose end time is greater
        that the current date.

        Since an event's date field is known to be a DateTimeField, the logic
        to support DateFields has been omitted.
        """
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(date + datetime.timedelta(days=1))

        return {
            'end__gte': since,
            'start__lt': until,
        }


class EventDetailView(generic.DetailView, generic.dates.BaseDateDetailView):
    model = Event
    date_field = 'start'
    allow_future = True


class RedirectCurrentMonth(generic.RedirectView):
    permanent = False
    pattern_name = "events:calendar-month"

    def get_redirect_url(self, *args, **kwargs):
        today = now().date()
        return super().get_redirect_url(year=today.year, month=today.month)
