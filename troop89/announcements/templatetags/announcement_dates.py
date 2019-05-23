#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import template

from ..models import Announcement

register = template.Library()

# Inspired by https://github.com/django/djangoproject.com/blob/master/blog/templatetags/weblog.py.
@register.inclusion_tag('announcements/includes/archive_year_month_listing.html')
def render_month_links():
    return {
        'announcement_dates': Announcement.objects.published().dates('pub_date', 'month', order='ASC'),
    }
