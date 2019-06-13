#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from typing import List, Tuple, Union

from django_json_ld.views import JsonLdContextMixin


class BreadcrumbJsonLdMixin(JsonLdContextMixin):
    """
    Mixin to create breadcrumb structured data in a view's context.

    See also the `BreadcrumbList specification`_ and `google's page on
    breadcrumb structured data`_.

    .. _BreadcrumbList specification: https://schema.org/BreadcrumbList
    .. _google's page on breadcrumb structured data: https://developers.google.com/search/docs/data-types/breadcrumb
    """
    breadcrumbs: List[Tuple[str, Union[str, dict]]] = None

    structured_data = {
        "@type": 'BreadcrumbList',
    }

    def __init__(self):
        super().__init__()

        if not self.breadcrumbs:
            self.breadcrumbs = []

    def get_structured_data(self):
        structured_data = super().get_structured_data()
        item_list = []
        breadcrumbs = self.get_breadcrumbs()
        for position, breadcrumb in enumerate(breadcrumbs, start=1):
            name, item = breadcrumb

            # If item is a string, make sure that it is an absolute url
            if isinstance(item, str):
                item = self.request.build_absolute_uri(item)
            else:
                # If item is a dict, make sure that its '@id' attribute is an
                # absolute url
                try:
                    item['@id'] = self.request.build_absolute_uri(item['id'])
                except LookupError:
                    raise TypeError("breadcrumb item must be a uri or a dict "
                                    "whose '@id' attribute is a uri")

            item_list.append({
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": item,
            })
        structured_data['itemListElement'] = item_list
        return structured_data

    def get_breadcrumbs(self):
        """
        Return the breadcrumbs to be rendered into structured data.

        Each 'breadcrumb' is a tuple containing 1) the breadcrumb name and 2)
        the breadcrumb item.

        Each breadcrumn item can beeither a string that represents a valid url
        (relative or absolute) or a dictionary of item properties that contains
        at least an '@id' attribute that is a valid url.
        """
        return self.breadcrumbs
