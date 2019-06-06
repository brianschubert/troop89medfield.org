#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from csp.decorators import csp_update
from django.contrib.flatpages.views import flatpage

# Rich text editor produces inline css for some features.
csp_exempt_flatpage = csp_update(
    STYLE_SRC=("'unsafe-inline'", "'self'")
)(flatpage)
