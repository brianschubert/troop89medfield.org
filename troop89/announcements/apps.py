#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig


class AnnouncementsConfig(AppConfig):
    name = 'troop89.announcements'
    label = 'announcements'
    verbose_name = 'Troop Announcements'
