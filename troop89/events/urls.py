from django.urls import path

from . import views

MONTH_FORMAT = '%m'

app_name = 'events'

urlpatterns = [
    path(
        '<int:year>/<int:month>/',
        views.CalendarMonthView.as_view(month_format=MONTH_FORMAT),
        name='calendar-month'
    ),
    path(
        '<int:year>/<int:month>/<int:day>/',
        views.EventDayView.as_view(month_format=MONTH_FORMAT),
        name='event-archive-day'
    ),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/',
        views.EventDetailView.as_view(month_format=MONTH_FORMAT),
        name='event-detail'
    ),
    path(
        'currentmonth/',
        views.RedirectCurrentMonth.as_view(),
        name='current-month'
    ),
    path(
        '<int:year>/<int:month>/events/',
        views.EventMonthView.as_view(month_format=MONTH_FORMAT),
        name='event-archive-month'
    ),
]
