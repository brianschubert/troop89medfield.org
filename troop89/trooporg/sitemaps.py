#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.sitemaps import Sitemap

from .models import Patrol, Term


class TermSitemap(Sitemap):
    changefreq = "never"
    priority = 0.4

    def items(self):
        return Term.objects.all()


class PatrolSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.4

    def items(self):
        return Patrol.objects.all()
