#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .base import *

# Better safe than sorry.
DEBUG = False

ALLOWED_HOSTS = [
] + SECRETS.get('ALLOWED_HOSTS', [])

# SecurityMiddleware settings

SECURE_SSL_REDIRECT = True

# 31536000 seconds = one year minimum for preload lists
SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = False  # For temporary stability verification

# CommonMiddleware settings

PREPEND_WWW = True
