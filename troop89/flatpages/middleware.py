#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf import settings
from django.http import Http404
from django.contrib.flatpages.middleware import FlatpageFallbackMiddleware

from .views import csp_exempt_flatpage


class CSPExemptFlatpageFallbackMiddleware(FlatpageFallbackMiddleware):
    """
    Copy of the standard flatpage middleware that modifies that CSP header for
    flatpage views.
    """

    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.
        try:
            return csp_exempt_flatpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response
