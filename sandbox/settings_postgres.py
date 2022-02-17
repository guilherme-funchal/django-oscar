from settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'oscar_travis',
        'USER': 'password',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '32768',
    }
}
