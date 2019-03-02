#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Term


class TermTest(TestCase):
    TODAY = datetime.date(2018, 6, 1)

    def test_term_start_may_not_overlap_with_another_term(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta
        end = self.TODAY + delta
        Term.objects.create(start=start, end=end)

        self.assertRaisesMessage(
            ValidationError,
            'Term overlaps with an existing term.',
            lambda: Term(start=self.TODAY, end=end + delta).clean()
        )

    def test_term_end_may_not_overlap_with_another_term(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta
        end = self.TODAY + delta
        Term.objects.create(start=start, end=end)

        self.assertRaisesMessage(
            ValidationError,
            'Term overlaps with an existing term.',
            lambda: Term(start=start - delta, end=self.TODAY).clean()
        )

    def test_term_may_not_contain_another_term(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta
        end = self.TODAY + delta
        Term.objects.create(start=start, end=end)

        self.assertRaisesMessage(
            ValidationError,
            'Term overlaps with an existing term.',
            lambda: Term(start=start - delta, end=end + delta).clean()
        )

    def test_term_start_may_overlap_with_another_end(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta
        end = self.TODAY + delta
        Term.objects.create(start=start, end=end)

        try:
            Term(start=end, end=end + delta).clean()
        except ValidationError:
            self.fail("term with start that overlaps with another term's end could not be created")

    def test_term_end_may_overlap_with_another_start(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta
        end = self.TODAY + delta
        Term.objects.create(start=start, end=end)

        try:
            Term(start=start - delta, end=start).clean()
        except ValidationError:
            self.fail("term with end that overlaps with another term's start could not be created")

    def test_term_overlapping_today_is_current(self):
        today = datetime.date.today()
        delta = datetime.timedelta(days=7)
        start = today - delta
        end = today + delta
        term = Term(start=start, end=end)
        self.assertTrue(term.is_current())

    def test_historic_term_not_current(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY - delta - delta
        end = self.TODAY - delta
        term = Term(start=start, end=end)
        self.assertFalse(term.is_current())

    def test_future_term_not_current(self):
        delta = datetime.timedelta(days=7)
        start = self.TODAY + delta + delta
        end = self.TODAY + delta
        term = Term(start=start, end=end)
        self.assertFalse(term.is_current())

    def test_term_end_may_not_predate_start(self):
        end = self.TODAY - datetime.timedelta(days=7)

        self.assertRaisesMessage(
            ValidationError,
            "Term start MUST occur before the term\'s end.",
            lambda: Term(start=self.TODAY, end=end).clean()
        )
