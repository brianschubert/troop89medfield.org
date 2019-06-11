#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import itertools
import os.path
import re
from typing import List, NamedTuple, Optional

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site

from ..models import HierarchicalFlatPage

register = template.Library()


@register.inclusion_tag('flatpages/includes/related_pages.html')
def render_related_pages(page: HierarchicalFlatPage, user=None):
    """
    Render a listing of pages with the same logical parent as the given page.

    Examples
    --------

    * ``/about/color/blue/`` would be in the related pages of ``/about/color/red/``.
    * ``/about/`` **would not** be in the related pages of ``/about/color/``.
    * ``/about/color/red/`` **would not** be in the related pages of ``/about/color/``.
    """
    current_site = Site.objects.get_current()

    flatpages = HierarchicalFlatPage.objects.filter(sites__id=current_site.pk)

    # If the provided user is not authenticated, or no user
    # was provided, filter the list to only public flatpages.
    if user:
        if not user.is_authenticated:
            flatpages = flatpages.filter(registration_required=False)
    else:
        flatpages = flatpages.filter(registration_required=False)

    return {
        'related_pages': flatpages.related_to(page),
        'current_page': page,
    }


class _PageHierarchyNode(NamedTuple):
    """Tuple representing a node in a hierarchy of flat pages."""
    uri: str
    page: Optional[HierarchicalFlatPage]
    children: List['_PageHierarchyNode']

    @property
    def title(self) -> str:
        if self.page:
            return self.page.title
        path = os.path.normpath(self.uri)
        return os.path.basename(path).replace('-', ' ').title()


class HierarchicalFlatpageTemplateNode(template.Node):
    def __init__(self, context_name, parent_page=None, user=None, depth=None):
        self.context_name = context_name
        if parent_page:
            self.parent_page = template.Variable(parent_page)
        else:
            self.parent_page = None
        if user:
            self.user = template.Variable(user)
        else:
            self.user = None
        if depth:
            self.depth = template.Variable(depth)
        else:
            self.depth = None

    def render(self, context):
        if 'request' in context:
            site_pk = get_current_site(context['request']).pk
        else:
            site_pk = settings.SITE_ID

        lookup_url = self.get_parent_url(context)

        if self.depth:
            depth = self.depth.resolve(context)
        else:
            depth = None

        flatpages = HierarchicalFlatPage.objects.children_for_url(
            url=lookup_url,
            depth=depth,
        )

        flatpages = flatpages.filter(sites__id=site_pk)

        # If the provided user is not authenticated, or no user
        # was provided, filter the list to only public flatpages.
        if self.user:
            user = self.user.resolve(context)
            if not user.is_authenticated:
                flatpages = flatpages.filter(registration_required=False)
        else:
            flatpages = flatpages.filter(registration_required=False)

        context[self.context_name] = list(_make_page_hierarchy(
            ordered_children=flatpages,
            common_prefix=lookup_url
        ))
        return ''

    def get_parent_url(self, context):
        if self.parent_page:
            parent_page = self.parent_page.resolve(context)
            try:
                lookup_url = parent_page.url
            except AttributeError:
                lookup_url = parent_page
        else:
            lookup_url = '/'
        return lookup_url


@register.tag
def get_flatpage_hierarchy(parser, token):
    """
    Retrieve a tree of flatpages representing the page hierarchy beginning at
    the specific page (or representing all flat pages if no parent page is
    specified). Populate the template context with them in a variable
    whose name is defined by the ``as`` clause.

    Like the standard ``get_flatpages`` tag from ``django.contrib.flatpages``,
    this tag retrieve the flatpage objects that are available for the current
    site and visible to the specific user (or visible to all users if no user is
    specified).

    An optional ``for`` clause controls the user whose permissions are used in
    determining which flatpages are visible.

    An optional argument, ``parent_page``, limits the returned flatpages to
    those beginning with a particular base URL. This argument can be a variable
    or a string, as it resolves from the template context.

    An optional argument, ``depth=n``, limits the returned flatpages to
    those who are at most the nth logical child of the ``parent_page``.
    This argument can be a variable or an integer, as it resolves from the
    template context.

    Syntax::

        {% get_flatpages ['url_starts_with' | flat_page_instance ]
            [for user] as context_name [depth=page_depth] %}

    Example usage::

        {% get_flatpage_hierarchy as flatpage_tree %}
        {% get_flatpage_hierarchy '/about/' as about_pages_tree %}
        {% get_flatpage_hierarchy about_page as about_pages_tree %}
        {% get_flatpage_hierarchy for some_user as flatpage_tree %}
        {% get_flatpage_hierarchy '/about/' as about_pages_tree depth=2 %}
        {% get_flatpage_hierarchy '/about/' as about_pages_tree depth=some_depth %}
    """
    syntax_re = (r'^(?:(?P<parent_page>["\'\w/]+) +)?(?:for +(?P<user>\w+) +)?'
                 r'as +(?P<context_name>\w+)(?: +depth=(?P<depth>\w+))?(?: +)?$')

    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        tag_name = token.contents.split()[0]
        raise template.TemplateSyntaxError(f'{tag_name} tag requires arguments')

    syntax_message = (f"{tag_name} expects a syntax of ['url_starts_with' | "
                      f"flat_page_instance ] [for user] as context_name "
                      f"[depth=page_depth]")

    match = re.match(syntax_re, args)

    if not match:
        raise template.TemplateSyntaxError(syntax_message)

    parent_page = match.group('parent_page')
    if parent_page and parent_page[0] in ('"', "'"):
        if not (parent_page[0] == parent_page[-1]):
            raise template.TemplateSyntaxError(
                f"{tag_name}: parent_page must be a flatpage object or a quoted string"
            )

    return HierarchicalFlatpageTemplateNode(**match.groupdict())


def _make_page_hierarchy(ordered_children, common_prefix) -> List[_PageHierarchyNode]:
    """
    Construct a tree representing the flatpage hierarchy of the
    ``ordered_pages``, starting at ``common_prefix``.

    This function assumes that ``ordered_pages`` is a sequence of
    HierarchicalFlatPages that are ordered lexicographically by their urls
    and that ``common_prefix`` *is* contained in all of the flatpages' urls.

    Note that if ``ordered_children`` contains the flatpage whose url is
    ``common_prefix``, the behavior of this function is not defined (i.e. it
    will error).
    """

    def get_next_child(prefix):
        """
        Return a callable that fetches uri of the next logical child after
        ``prefix`` in the uri of a flat page.

        For example, the callable ``get_next_child('/about/')`` will return
        ``/about/contact/`` when call on the flatpage with the url
        ``/about/contact/webmaster``.
        """
        pattern = re.compile(rf'{prefix}[^/]+/')

        def _get_next_child(page: HierarchicalFlatPage):
            # Assume that the prefix is contained in the url
            return pattern.match(page.url_with_slash).group(0)

        return _get_next_child

    grouping = itertools.groupby(ordered_children, get_next_child(common_prefix))

    for prefix, children in grouping:
        children = list(children)

        # If a page exists for the prefix, it will be the first page in the
        # children list since the pages were pre-sorted by url
        if children[0].url == prefix:
            page = children.pop(0)
        else:
            page = None  # No flatpage exists for the prefix
        if children:
            children = list(_make_page_hierarchy(children, prefix))
        yield _PageHierarchyNode(uri=prefix, children=children, page=page)
