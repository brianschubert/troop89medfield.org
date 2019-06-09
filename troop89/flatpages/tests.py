#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.test import TestCase

from .models import HierarchicalFlatPage


class HierarchicalFlatPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.flatpages = HierarchicalFlatPage.objects.bulk_create([
            HierarchicalFlatPage(url='/about/'),
            HierarchicalFlatPage(url='/about/contact/'),
            HierarchicalFlatPage(url='/about/contact/scoutmaster/'),
            HierarchicalFlatPage(url='/about/contact/webmaster/'),
            HierarchicalFlatPage(url='/about/merit-badges/bird-study/'),
            HierarchicalFlatPage(url='/about/merit-badges/cooking/'),
        ])
        cls.about_page = cls.flatpages[0]

    def test_parent_url_for_child_page(self):
        contact_page = self.flatpages[1]
        self.assertEqual(str(contact_page.parent_url), '/about')

    def test_parent_url_no_parent(self):
        self.assertEqual(str(self.about_page.parent_url), '/')

    def test_children_pages_depth_1(self):
        children = self.about_page.children_pages()

        self.assertEqual(len(children), 1)

        self.assertEqual(
            children.get(),
            HierarchicalFlatPage.objects.get(url='/about/contact/'),
        )

    def test_children_pages_depth_2(self):
        children = self.about_page.children_pages(depth=2)

        self.assertEqual(len(children), 5)

        self.assertEqual(
            list(children),
            self.flatpages[1:],
        )

    def test_children_pages_depth_2_ignore_parents(self):
        children = self.about_page.children_pages(depth=2, include_parents=False)

        self.maxDiff = None

        self.assertEqual(len(children), 4)

        self.assertEqual(
            list(children),
            self.flatpages[2:],
        )

    def test_parent_pages_child_with_all_parents(self):
        scoutmaster_page = self.flatpages[2]

        parents = scoutmaster_page.parent_pages
        self.assertEqual(len(parents), 2)

        self.assertEqual(
            # pathlib convention of deepest-first is followed
            list(reversed(parents)),
            self.flatpages[:2],
        )

    def test_parent_pages_child_with_partial_parents(self):
        cooking_page = self.flatpages[5]

        parents = cooking_page.parent_pages
        self.assertEqual(len(parents), 1)

        self.assertEqual(
            parents.get(),
            self.flatpages[0],
        )

    def test_parent_pages_no_parents(self):
        about_page = self.flatpages[5]

        parents = about_page.parent_pages
        self.assertEqual(len(parents), 1)

        self.assertEqual(
            parents.get(),
            self.flatpages[0],
        )
