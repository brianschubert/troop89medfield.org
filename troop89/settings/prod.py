from .base import *

# Better safe than sorry.
DEBUG = False

ALLOWED_HOSTS = [
] + SECRETS.get('ALLOWED_HOSTS', [])
