#  Copyright (c) 2018, 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views import generic

from troop89.date_range.views import DayDateRangeView, MonthDateRangeView
from troop89.json_ld.views import BreadcrumbJsonLdMixin
from troop89.trooporg.models import Member
from . import utils
from .models import Event
from .templatetags import event_flatpage


class EventBreadcrumbMixin(BreadcrumbJsonLdMixin):
    """
    Mixin for Event views to set breadcrumb structured data the view's context.
    """

    def __init__(self, **kwargs):
        """
        Most of the event views rely on kwargs to set instance attributes such
        as ``self.month_format``. However, ``JsonLdContextMixin``, which
        BreadcrumbJsonLdMixin inherits from, does not accept any kwargs and
        therefore prevents these arguments from propagating to ``View``'s
        ``__init__`` method.

        This this issue is mitigated by explicitly calling ``View.__init__()``
        before ``super().__init__()``, which presumptively converts all kwargs into
        attributes, removing the need to pass the kwargs to parent ``__init__()``s.
        """
        generic.View.__init__(self, **kwargs)
        super().__init__()

    @staticmethod
    def make_common_breadcrumbs(date: datetime):
        return [
            (
                "Calendar",
                reverse('events:calendar-month', args=(date.year, date.month)),
            ),
            (
                date.strftime("%B %Y Events"),
                reverse('events:event-archive-month', args=(date.year, date.month)),
            ),
        ]


class EventMonthView(EventBreadcrumbMixin, MonthDateRangeView):
    model = Event
    allow_empty = True
    allow_future = True
    date_field_start = 'start'
    date_field_end = 'end'
    context_object_name = 'events'

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        date = datetime(self.get_year(), self.get_month(), 1)
        breadcrumbs += self.make_common_breadcrumbs(date)
        return breadcrumbs


class CalendarMonthView(EventMonthView):
    template_name = 'events/calendar_month.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        year = self.get_year()
        month = self.get_month()
        if object_list is None:
            object_list = []

        calendar = utils.EventCalendar(year, month, object_list)
        context = super().get_context_data(**kwargs)
        context['calendar'] = calendar

        return context

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()

        date = datetime(self.get_year(), self.get_month(), 1)
        breadcrumbs[-1] = (
            date.strftime("%B %Y Calendar"),
            reverse('events:calendar-month', args=(date.year, date.month)),
        )
        return breadcrumbs


class EventDayView(EventBreadcrumbMixin, DayDateRangeView):
    model = Event
    allow_empty = True
    allow_future = True
    date_field_start = 'start'
    date_field_end = 'end'
    context_object_name = 'events'

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        date = datetime(self.get_year(), self.get_month(), self.get_day())
        breadcrumbs += self.make_common_breadcrumbs(date)
        breadcrumbs.append((
            date.strftime("%a. %B %d"),
            reverse('events:event-archive-day', args=(date.year, date.month, date.day)),
        ))
        return breadcrumbs


class EventDetailView(EventBreadcrumbMixin, generic.DetailView, generic.dates.BaseDateDetailView):
    model = Event
    date_field = 'start'
    allow_future = True

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()

        date = timezone.localdate(self.object.start)

        breadcrumbs += self.make_common_breadcrumbs(date)
        breadcrumbs += [
            (
                date.strftime("%a. %B %d"),
                reverse('events:event-archive-day', args=(date.year, date.month, date.day)),
            ),
            (
                self.object.title,
                reverse('events:event-detail', args=(date.year, date.month, date.day, self.object.slug)),
            ),
        ]
        return breadcrumbs


class RedirectCurrentMonth(generic.RedirectView):
    permanent = False
    pattern_name = "events:calendar-month"

    def get_redirect_url(self, *args, **kwargs):
        today = localtime(now()).date()
        return super().get_redirect_url(year=today.year, month=today.month)


@method_decorator(staff_member_required, name='dispatch')
class RedirectAddEventReportFlatpage(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    generic.detail.SingleObjectMixin,
    generic.RedirectView,
):
    """
    View to redirect the user to a prepopulated form to add an "Event report"
    flatpage for a specific event.

    This view encodes the form data for creating an "Event report" flatpage
    in the query string of the request uri. This method was chosen so that
    default form data could be provided when creating a flatpage without the
    ``flatpages`` app being aware of the ``events`` app.

    Note that this view relies on the existence of PositionType instances
    from the ``trooporg`` app with the titles 'Senior Patrol Leader'
    and 'Assistant Senior Patrol Leader'.
    """
    EVENT_REPORT_CONTENT_FORMAT = """\
    <h1>Event Report for <a href="{url}">{title}</a></h1>
    <p><b>Date: </b> {event_date}</p>
    <p><b>SPL: </b> {spl}</p>
    <p><b>ASPLs: </b> {aspl}</p>
    <p>Please write your report for this event here...</p>
    <p></p>
    <div class="meta"> Posted by {user} on {post_date}.</div>
    """
    DATE_FORMAT = '%B %d, %Y'
    TIME_FORMAT = '%I:%M %p'

    model = Event
    permanent = False
    pattern_name = 'admin:troop89_flatpages_hierarchicalflatpage_add'
    permission_required = 'troop89_flatpages.add_hierarchicalflatpage'

    def get_redirect_url(self, *args, **kwargs):
        event = self.get_object()
        # Set up default values for flatpage form fields.
        query = QueryDict(mutable=True)
        query['url'] = event_flatpage.make_event_report_url(event)
        query['title'] = f'{event.start.strftime("%B")} - {event.title}'
        query['content'] = self.EVENT_REPORT_CONTENT_FORMAT.format(
            url=event.get_absolute_url(),
            title=event.title,
            # Refetch the user as a Member instance to access safe display logic
            user=Member.objects.get(pk=self.request.user.pk).get_safe_display(),
            post_date=timezone.now().strftime(self.DATE_FORMAT),
            event_date=utils.render_datetime_range(event.start, event.end, self.DATE_FORMAT, self.TIME_FORMAT),
            spl=_render_incumbent_names(
                utils.fetch_event_position_incumbents(event, 'Senior Patrol Leader')
            ),
            aspl=_render_incumbent_names(
                utils.fetch_event_position_incumbents(event, 'Assistant Senior Patrol Leader')
            ),
        )
        return ''.join([
            # Do not include the args when calling the parent method since
            # `admin:troop89_flatpages_hierarchicalflatpage_add` expects no
            # arguments.
            super().get_redirect_url(),
            '?',
            query.urlencode(),
        ])


def _render_incumbent_names(incumbents):
    """Render the list of Member instances into a string of safe names."""
    return ' and '.join(m.get_safe_display() for m in incumbents)
