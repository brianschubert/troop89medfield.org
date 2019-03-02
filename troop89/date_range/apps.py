#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig


class DateRangeConfig(AppConfig):
    name = 'troop89.date_range'
    label = 'date_range'
    verbose_name = 'Date Range Views'
