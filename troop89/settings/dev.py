#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "troop89.localhost",
] + SECRETS.get('ALLOWED_HOSTS', [])

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1'
]

CSP_REPORT_ONLY = True

# For django debug toolbar
CSP_SCRIPT_SRC = ("'self'", 'ajax.googleapis.com')

CSP_IMG_SRC += ('data:',)
