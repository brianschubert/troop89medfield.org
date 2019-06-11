#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
import unittest

import pytz
from django.shortcuts import reverse
from django.test import TestCase, override_settings

from .util import local_date_range


class DateRangeTest(unittest.TestCase):
    TIMEZONE = pytz.utc

    def test_vary_by_whole_days(self):
        d1 = datetime.datetime(2018, 1, 1, tzinfo=self.TIMEZONE)
        d2 = datetime.datetime(2018, 1, 3, tzinfo=self.TIMEZONE)

        expected = [
            datetime.date(2018, 1, 1),
            datetime.date(2018, 1, 2),
            datetime.date(2018, 1, 3),
        ]

        self.assertEqual(local_date_range(d1, d2, self.TIMEZONE), expected)

    def test_same_date(self):
        d = datetime.datetime(2018, 1, 1, tzinfo=self.TIMEZONE)

        self.assertEqual(local_date_range(d, d, self.TIMEZONE), [d.date()])

    def test_end_of_day(self):
        d1 = datetime.datetime(2018, 1, 1, 0, 0, 0, 0, tzinfo=self.TIMEZONE)
        d2 = datetime.datetime(2018, 1, 1, 23, 59, 59, 999999, tzinfo=self.TIMEZONE)

        self.assertEqual(local_date_range(d1, d2, self.TIMEZONE), [d1.date()])

        next_day = d2 + datetime.timedelta(microseconds=1)

        self.assertEqual(len(local_date_range(d1, next_day)), 2)

    def test_end_before_start(self):
        d1 = datetime.datetime(2018, 1, 1, tzinfo=self.TIMEZONE)
        d2 = datetime.datetime(2018, 1, 3, tzinfo=self.TIMEZONE)

        self.assertEqual(local_date_range(d2, d1, self.TIMEZONE), [])


@override_settings(SECURE_SSL_REDIRECT=False, PREPEND_WWW=False)
class CalendarMonthViewTestCase(TestCase):
    fixtures = ("events.json",)

    def test_fetch_single_event_in_month(self):
        response = self.client.get('/calendar/2018/06/')
        events = response.context['object_list']
        self.assertEqual(len(events), 1)

    def test_fetch_event_spanning_month(self):
        response_july = self.client.get('/calendar/2018/07/')
        response_august = self.client.get('/calendar/2018/08/')

        for response in (response_july, response_august):
            self.assertTrue(any(e.title == 'Camp Squanto' for e in response.context['object_list']))


@override_settings(SECURE_SSL_REDIRECT=False, PREPEND_WWW=False)
class EventDayViewTestCase(TestCase):
    fixtures = ("events.json",)

    def test_fetch_event_starting_on_day(self):
        response = self.client.get('/calendar/2018/07/07/')
        titles = [e.title for e in response.context['object_list']]
        self.assertListEqual(titles, ['A Trip'])

    def test_fetch_event_ending_on_day(self):
        response = self.client.get('/calendar/2018/07/08/')
        titles = [e.title for e in response.context['object_list']]
        self.assertListEqual(titles, ['A Trip'])

    def test_fetch_event_spanning_day_starting_in_same_month(self):
        response = self.client.get('/calendar/2018/07/30/')
        titles = [e.title for e in response.context['object_list']]
        self.assertListEqual(titles, ['Camp Squanto'])

    def test_fetch_event_spanning_day_starting_in_different_month(self):
        response = self.client.get('/calendar/2018/08/03/')
        titles = [e.title for e in response.context['object_list']]
        self.assertListEqual(titles, ['Camp Squanto'])


@override_settings(SECURE_SSL_REDIRECT=False, PREPEND_WWW=False)
class RedirectCurrentMonthTestCase(TestCase):

    def test_redirect_current_month(self):
        response = self.client.get('/calendar/currentmonth/', follow=False)
        today = datetime.date.today()
        expected_url = reverse("events:calendar-month", args=(today.year, today.month))
        self.assertRedirects(response, expected_url)
