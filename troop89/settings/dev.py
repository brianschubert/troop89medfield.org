from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "troop89.testing"
] + SECRETS.get('ALLOWED_HOSTS', [])

STATIC_ROOT = os.path.join(BASE_DIR, "../static")
