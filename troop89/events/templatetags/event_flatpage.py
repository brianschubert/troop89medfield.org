#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import template
from django.urls import reverse
from django.utils import timezone

from troop89.flatpages.models import HierarchicalFlatPage

register = template.Library()

EVENT_REPORT_URL_STUB = '/records/event-reports'


@register.inclusion_tag('events/includes/event_flatpage_link.html')
def render_flatpage_link(event, user) -> dict:
    """
    Render an anchor to the "Event Report" flatpage associated with the
    specific event. If no such page exists, and the given user has permission,
    render an anchor to a prepopulated form to add an "Event report" flatpage.
    """
    try:
        flatpage_url = make_event_report_url(event)
        flatpage = HierarchicalFlatPage.objects.get(url=flatpage_url)
    except HierarchicalFlatPage.DoesNotExist:
        flatpage = None

    if not flatpage and user.is_staff and user.has_perm('troop89_flatpages.add_hierarchicalflatpage'):
        creation_url = reverse('events:event-redirect-add-report-flatpage', args=(event.pk,))
    else:
        creation_url = None
    return {
        'flatpage': flatpage,
        'creation_url': creation_url,
    }


def make_event_report_url(event):
    """
    Render the URL for the 'Event Report' flatpage that corresponds with the
    given Event.
    """
    start = timezone.localtime(event.start)
    return f'{EVENT_REPORT_URL_STUB}/{start.year}/{event.slug}/'
