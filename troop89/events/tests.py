import datetime
import unittest
import pytz

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
