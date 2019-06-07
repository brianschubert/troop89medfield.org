#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pathlib import PurePath

from django.contrib.flatpages.models import FlatPage
from django.db import models
from django.db.models.functions import Length
from django.db.utils import cached_property


class HierarchicalFlatPageQuerySet(models.QuerySet):

    def related_to(self, page: 'HierarchicalFlatPage'):
        related_stem = page.parent_url

        # If the page has no parent (e.g /about/), do not include
        # a related stem in the url regex so that all other pages
        # with no parent are matched.
        if related_stem == '/':
            related_stem = ''

        return self.filter(url__regex=rf"^{related_stem}/[^/]+/$")


class HierarchicalFlatPage(FlatPage):
    objects = HierarchicalFlatPageQuerySet.as_manager()

    class Meta:
        proxy = True
        verbose_name = 'flat page'
        verbose_name_plural = 'flat pages'

    @property
    def parent_url(self) -> PurePath:
        """
        Return the url of this page's logical parent.

        **Note**: the url *will* contain a leading slash and *will not*
        contain a trailing slash.
        """
        return PurePath(self.url).parent

    @property
    def _url_with_slash(self):
        """Return this page's url with a trailing if one is missing"""
        if self.url.endswith('/'):
            return self.url
        return f'{self.url}/'

    @cached_property
    def parent_pages(self):
        """
        Return the flatpages which are the logical parents of this page.
        """
        # Make a list of the urls that precede this page, excluding the root '/'
        parents = [f'{uri}/' for uri in PurePath(self.url).parents][:-1]

        return HierarchicalFlatPage.objects.filter(url__in=parents).order_by(Length('url').desc())

    def children_pages(self, depth: int = 1, include_parents: bool = True):
        if include_parents:
            # allow anywhere between 1 and `depth` subdirectories
            depth = f"1,{depth}"
        filter_pattern = rf"^{self._url_with_slash}([^/]+/){{{depth}}}$"
        return HierarchicalFlatPage.objects.filter(url__regex=filter_pattern)
