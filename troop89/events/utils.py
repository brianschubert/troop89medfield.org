#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import calendar
import collections
from datetime import date, datetime, timedelta
from typing import Dict, List, NamedTuple, Sequence

from django.utils import timezone

from .models import Event

FIRST_DAY_OF_WEEK = 6


def local_date_range(start: datetime, end: datetime, tz=None) -> List[date]:
    """
    Return a list of every date that occurs between two aware datetimes.
    """
    start_date = timezone.localtime(start, tz).date()
    delta = timezone.localtime(end, tz).date() - start_date

    return [start_date + timedelta(days=d) for d in range(delta.days + 1)]


def _group_by_date(events: Sequence[Event]) -> Dict[date, List[Event]]:
    date_map = collections.defaultdict(list)

    for event in events:
        for day in event.local_date_range():
            date_map[day].append(event)

    return date_map


class EventCalendar:
    class DateEntry(NamedTuple):
        date: date
        events: List[Event]

    def __init__(self, year: int, month: int, events: Sequence[Event] = None, title: str = None):
        self.year = year
        self.month = month
        self.events = events
        self._title = title

    @property
    def title(self):
        if self._title is None:
            return '{} {}'.format(calendar.month_name[self.month], self.year)
        return self._title

    def events_by_month_dates(self) -> List[List[DateEntry]]:
        events_by_date = _group_by_date(self.events)
        cal = calendar.Calendar(FIRST_DAY_OF_WEEK).monthdatescalendar(self.year, self.month)
        result = []
        for week in cal:
            week_events = []
            for day in week:
                week_events.append(self.DateEntry(day, events_by_date.get(day, [])))
            result.append(week_events)

        return result
