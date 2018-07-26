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
