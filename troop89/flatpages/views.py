#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from csp.decorators import csp_update
from django.conf import settings
from django.contrib.flatpages import views as flatpage_views
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404

from .models import HierarchicalFlatPage


# Rich text editor produces inline css for some features.
@csp_update(STYLE_SRC=("'unsafe-inline'", "'self'"), FRAME_SRC="https://meritbadge.org/wiki/")
def hierarchical_flatpage(request, url):
    """
    Copy of the standard public interface to the flat page view that integrates
    HierarchicalFlatPages.
    """
    if not url.startswith('/'):
        url = '/' + url
    site_id = get_current_site(request).id
    try:
        f = get_object_or_404(HierarchicalFlatPage, url=url, sites=site_id)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(HierarchicalFlatPage, url=url, sites=site_id)
            return HttpResponsePermanentRedirect(f'{request.path}/')
        else:
            raise
    return flatpage_views.render_flatpage(request, f)
