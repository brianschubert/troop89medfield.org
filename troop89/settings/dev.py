from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "troop89.testing"
] + SECRETS.get('ALLOWED_HOSTS', [])

