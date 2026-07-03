import os
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}