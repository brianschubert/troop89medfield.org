#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase

from troop89.auth.models import User
from .models import HierarchicalFlatPage
from .templatetags.flatpage_hierarchy import _make_page_hierarchy


class HierarchicalFlatPageTests(TestCase):
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


class HierarchicalFlatPageTemplateTagTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(pk=1)
        cls.flatpages = HierarchicalFlatPage.objects.bulk_create([
            HierarchicalFlatPage(url='/about/', title='Has a Title'),
            HierarchicalFlatPage(url='/about/contact/'),
            HierarchicalFlatPage(url='/about/contact/scoutmaster/'),
            HierarchicalFlatPage(url='/about/contact/webmaster/'),
            HierarchicalFlatPage(url='/about/merit-badges/bird-study/'),
            HierarchicalFlatPage(url='/about/merit-badges/cooking/'),
            HierarchicalFlatPage(url='/about/private/', registration_required=True),
        ])
        for page in cls.flatpages:
            page.sites.set([cls.site])
            page.save()

    def test_make_page_hierarchy_builds_correct_tree(self):
        page_tree = list(_make_page_hierarchy(self.flatpages[1:], '/about/'))

        self.assertEqual(
            [node.uri for node in page_tree],
            ['/about/contact/', '/about/merit-badges/', '/about/private/'],
        )

        contact_pages = page_tree[0].children
        merit_badge_pages = page_tree[1].children

        self.assertEqual(
            [node.uri for node in contact_pages],
            ['/about/contact/scoutmaster/', '/about/contact/webmaster/']
        )
        self.assertEqual(
            [node.uri for node in merit_badge_pages],
            ['/about/merit-badges/bird-study/', '/about/merit-badges/cooking/']
        )

    def test_make_page_hierarchy_handles_missing_middle_page(self):
        page_tree = list(_make_page_hierarchy(self.flatpages[3:6], '/about/'))

        self.assertEqual(
            [(node.uri, node.page) for node in page_tree],
            [('/about/contact/', None), ('/about/merit-badges/', None)],
        )

        contact_pages = page_tree[0].children
        merit_badge_pages = page_tree[1].children

        self.assertEqual(
            [node.uri for node in contact_pages],
            ['/about/contact/webmaster/'],
        )
        self.assertEqual(
            [node.uri for node in merit_badge_pages],
            ['/about/merit-badges/bird-study/', '/about/merit-badges/cooking/']
        )

    def test_get_flatpage_hierarchy(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context())
        expected = ("/about/"
                    "   /about/contact/"
                    "       /about/contact/scoutmaster/"
                    "       /about/contact/webmaster/"
                    "   /about/merit-badges/"
                    "       /about/merit-badges/bird-study/"
                    "       /about/merit-badges/cooking/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_base_page(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy '/about/' as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for child in parent.children %}"
            "   {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context())
        expected = ("/about/contact/"
                    "   /about/contact/scoutmaster/"
                    "   /about/contact/webmaster/"
                    "/about/merit-badges/"
                    "   /about/merit-badges/bird-study/"
                    "   /about/merit-badges/cooking/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_variable_base_page(self):
        about_page = self.flatpages[0]
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy about_page as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for child in parent.children %}"
            "   {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'about_page': about_page
        }))
        expected = ("/about/contact/"
                    "   /about/contact/scoutmaster/"
                    "   /about/contact/webmaster/"
                    "/about/merit-badges/"
                    "   /about/merit-badges/bird-study/"
                    "   /about/merit-badges/cooking/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_for_anon_user(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy for anon_user as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'anon_user': AnonymousUser()
        }))
        expected = ("/about/"
                    "   /about/contact/"
                    "       /about/contact/scoutmaster/"
                    "       /about/contact/webmaster/"
                    "   /about/merit-badges/"
                    "       /about/merit-badges/bird-study/"
                    "       /about/merit-badges/cooking/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_for_user(self):
        some_user = User.objects.create_user('testuser', 'test@example.com', 'password')
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy for some_user as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'some_user': some_user
        }))
        expected = ("/about/"
                    "   /about/contact/"
                    "       /about/contact/scoutmaster/"
                    "       /about/contact/webmaster/"
                    "   /about/merit-badges/"
                    "       /about/merit-badges/bird-study/"
                    "       /about/merit-badges/cooking/"
                    "   /about/private/")  # Note access to private page
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_base_page_for_anon_user(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy '/about/' for anon_user as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'anon_user': AnonymousUser()
        }))
        expected = ("/about/contact/"
                    "   /about/contact/scoutmaster/"
                    "   /about/contact/webmaster/"
                    "/about/merit-badges/"
                    "   /about/merit-badges/bird-study/"
                    "   /about/merit-badges/cooking/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_base_page_for_user(self):
        some_user = User.objects.create_user('testuser', 'test@example.com', 'password')
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy '/about/' for some_user as flatpage_tree %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'some_user': some_user
        }))
        expected = ("/about/contact/"
                    "   /about/contact/scoutmaster/"
                    "   /about/contact/webmaster/"
                    "/about/merit-badges/"
                    "   /about/merit-badges/bird-study/"
                    "   /about/merit-badges/cooking/"
                    "/about/private/")  # Note access to private page
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_depth(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy as flatpage_tree depth=2 %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context())
        # Note no entry for /merit-badges/ since no base page exists
        expected = ("/about/"
                    "   /about/contact/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_variable_depth(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy as flatpage_tree depth=some_depth %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'some_depth': 2
        }))
        # Note no entry for /merit-badges/ since no base page exists
        expected = ("/about/"
                    "   /about/contact/")
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_base_page_and_depth_for_user(self):
        some_user = User.objects.create_user('testuser', 'test@example.com', 'password')
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy '/about/' for some_user as flatpage_tree depth=1%}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'some_user': some_user
        }))
        # Note no entry for /merit-badges/ since no base page exists
        expected = ("/about/contact/"
                    "/about/private/")  # Note access to private page
        self.assertEqual(out, expected)

    def test_get_flatpage_hierarchy_with_base_page_and_depth_for_anon_user(self):
        out = Template(
            "{% load flatpage_hierarchy %}"
            "{% get_flatpage_hierarchy '/about/' for anon_user as flatpage_tree depth=1 %}"
            ""
            "{% for parent in flatpage_tree %}"
            "{{ parent.uri }}"
            "{% for middle in parent.children %}"
            "   {{ middle.uri }}"
            "{% for child in middle.children %}"
            "       {{ child.uri }}"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'anon_user': AnonymousUser()
        }))
        # Note no entry for /merit-badges/ since no base page exists
        expected = "/about/contact/"
        self.assertEqual(out, expected)
