#  Copyright (c) 2018 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model to enable future expansion.

    For now, now additional model-level functionality has been added. Users
    stand as is.

    Defined as recommended by the `django authentication docs`_.

    .. _django authentication docs: https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    """
    pass
