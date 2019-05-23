#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.urls import path

from . import views

MONTH_FORMAT = '%m'

app_name = 'announcements'

urlpatterns = [
    path('', views.AnnouncementIndexView.as_view(), name='announcement-index'),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/',
        views.AnnouncementDetailView.as_view(month_format=MONTH_FORMAT),
        name='announcement-detail',
    ),
    path(
        '<int:year>/',
        views.AnnouncementYearView.as_view(),
        name='announcement-archive-year',
    ),
    path(
        '<int:year>/<int:month>/',
        views.AnnouncementMonthView.as_view(month_format=MONTH_FORMAT),
        name='announcement-archive-month',
    ),
]
