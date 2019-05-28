#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta

from django import template
from django.utils import timezone

from ..models import Event

register = template.Library()


@register.inclusion_tag('events/includes/event_listing.html')
def render_upcoming_events(limit: int = None, **kwargs) -> dict:
    """
    Render a list of the next `limit` upcoming events.


    All `kwargs` are used to create a `timedelta` that determines the upper
    bound for upcoming events.

    All events whose `end_date` is greater than or equal to the current time and
    whose `start_date` is less than or equal to the **date** corresponding to the
    current date plus the timedelta specified by the `kwargs` will be returned.

    As an example, `render_upcoming_events(3, days=1)` will return the first 3
    events whose start time is less than or equal to midnight tonight (i.e.
    time 00:00 tomorrow) and whose end time has not yet occurred.
    """
    if not kwargs:
        raise ValueError('render_upcoming_events kwargs MUST not be empty')
    today = timezone.now()
    end_date = timezone.localtime(today + timedelta(**kwargs))
    end_date = end_date.replace(hour=0, minute=0)  # Compare only the date of the end bound
    return {
        'events': Event.objects.filter(start__lte=end_date, end__gte=today)
    }
