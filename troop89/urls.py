#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""troop89 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path('', TemplateView.as_view(template_name='maintenance.html'), name='home'),
    path('base/', TemplateView.as_view(template_name='base.html'), name='base'),
    path('base-unary/', TemplateView.as_view(template_name='base_unary.html'), name='base_unary'),
    path('base-binary/', TemplateView.as_view(template_name='base_binary.html'), name='base_binary'),
    path('calendar/', include('troop89.events.urls', namespace='events')),
    path('members/', include('troop89.trooporg.urls', namespace='trooporg')),
    path('announcements/', include('troop89.announcements.urls', namespace='announcements')),
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('csp/', include('cspreports.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
