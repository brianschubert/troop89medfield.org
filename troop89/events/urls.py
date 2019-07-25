#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
    path(
        'report/<int:pk>/',
        views.RedirectAddEventReportFlatpage.as_view(),
        name='event-redirect-add-report-flatpage'
    ),
]
