#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pathlib import PurePath

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.functions import Length
from django.db.utils import cached_property


class BaseHierarchicalFlatPageManager(models.Manager):

    def children_for_url(self, url, depth: int = None, include_parents: bool = True):
        """
        Return the flatpages which are the logical children of the given url.

        The provided url *does not* have to be a valid flatpage.
        """
        url = _ensure_trailing_slash(url)

        if depth:
            if include_parents:
                # Allow anywhere between 1 and `depth` subdirectories
                depth_quantifier = f"1,{depth}"
            else:
                depth_quantifier = depth
        else:
            depth_quantifier = '1,'

        filter_pattern = rf"^{url}([^/]+/){{{depth_quantifier}}}$"
        return self.get_queryset().filter(url__regex=filter_pattern)


class HierarchicalFlatPageQuerySet(models.QuerySet):

    def related_to(self, page: 'HierarchicalFlatPage'):
        related_stem = page.parent_url

        # If the page has no parent (e.g /about/), do not include
        # a related stem in the url regex so that all other pages
        # with no parent are matched.
        if str(related_stem) == '/':
            related_stem = ''

        return self.exclude(pk=page.pk).filter(url__regex=rf"^{related_stem}/[^/]+/$")


HierarchicalFlatPageManager = BaseHierarchicalFlatPageManager.from_queryset(HierarchicalFlatPageQuerySet)


class HierarchicalFlatPage(FlatPage):
    objects = HierarchicalFlatPageManager()

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
    def url_with_slash(self) -> str:
        """Return this page's url with a trailing if one is missing"""
        return _ensure_trailing_slash(self.url)

    @cached_property
    def parent_pages(self):
        """
        Return the flatpages which are the logical parents of this page, deepest first.
        """
        # Make a list of the urls that precede this page, excluding the root '/'
        parents = [f'{uri}/' for uri in PurePath(self.url).parents][:-1]

        return HierarchicalFlatPage.objects.filter(url__in=parents).order_by(Length('url').desc())

    def children_pages(self, depth: int = 1, include_parents: bool = True):
        """
        Return the flatpages which are the logical children of this page.
        """
        return HierarchicalFlatPage.objects.children_for_url(self.url, depth, include_parents)

    @property
    def sd_breadcrumb(self) -> dict:
        """Return this page's breadcrumb trail as a structured data dict."""
        domain = Site.objects.get_current().domain
        protocol = 'https' if settings.SECURE_SSL_REDIRECT else 'http'
        item_list = []

        for position, page in enumerate(reversed(self.parent_pages), start=1):
            item_list.append({
                "@type": "ListItem",
                "position": position,
                "name": page.title,
                # Absolute url construction as recommended in the Django docs:
                # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#getting-the-current-domain-for-full-urls
                "item": f'{protocol}://{domain}{page.url}',
            })
        item_list.append({
                "@type": "ListItem",
                "position": len(self.parent_pages) + 1,
                "name": self.title,
                "item": f'{protocol}://{domain}{self.url}',
            })
        return {
            "@context": "https://schema.org",
            "@type": 'BreadcrumbList',
            "itemListElement": item_list,
        }


def _ensure_trailing_slash(url: str) -> str:
    """Return the given url with a trailing if one is missing"""
    if url.endswith('/'):
        return url
    return f'{url}/'
