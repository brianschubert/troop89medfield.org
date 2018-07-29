from datetime import date, datetime, tzinfo
from typing import Union

from django import template
from django.utils.timezone import localtime, now

from ..models import Event

register = template.Library()

TIME_FORMAT = '%I:%M %p'


@register.filter
def is_today(day: Union[datetime, date]) -> bool:
    today = now().date()
    try:
        return day.date() == today
    except AttributeError:
        return day == today


@register.simple_tag
def event_date_overlap(event: Event, day: date, timezone: tzinfo = None) -> str:
    starts_today = localtime(event.start, timezone).date() == day
    ends_today = localtime(event.end, timezone).date() == day

    start_local = localtime(event.start).strftime(TIME_FORMAT)
    end_local = localtime(event.end).strftime(TIME_FORMAT)

    if starts_today:
        if ends_today:
            return start_local + ' - ' + end_local
        else:
            return 'after ' + start_local
    elif event.start.date() < day:  # event already began
        if ends_today:
            return 'until ' + end_local
        else:
            return 'all day'
    return ''


@register.simple_tag
def repeat_str(s: str, count: int) -> str:
    return s * count
