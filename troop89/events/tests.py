import datetime
import unittest

from .util import local_date_range


class DateRangeTest(unittest.TestCase):

    def test_vary_by_whole_days(self):
        d1 = datetime.datetime(2018, 1, 1)
        d2 = datetime.datetime(2018, 1, 3)

        expected = [
            datetime.date(2018, 1, 1),
            datetime.date(2018, 1, 2),
            datetime.date(2018, 1, 3),
        ]

        self.assertEqual(local_date_range(d1, d2), expected)

    def test_same_date(self):
        d = datetime.datetime(2018, 1, 1)

        self.assertEqual(local_date_range(d, d), [d.date()])

    def test_end_of_day(self):
        d1 = datetime.datetime(2018, 1, 1, 0, 0, 0, 0)
        d2 = datetime.datetime(2018, 1, 1, 23, 59, 59, 999999)

        self.assertEqual(local_date_range(d1, d2), [d1.date()])

        next_day = d2 + datetime.timedelta(microseconds=1)

        self.assertEqual(len(local_date_range(d1, next_day)), 2)

    def test_end_before_start(self):
        d1 = datetime.datetime(2018, 1, 1)
        d2 = datetime.datetime(2018, 1, 3)

        self.assertEqual(local_date_range(d2, d1), [])
