from retrato.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

PHOTOS_ROOT_DIR = '/meus_arquivos/photos/'
BASE_CACHE_DIR = "/var/cache/"
REQUIRE_AUTHENTICATION = True

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.mysql',
        'NAME':         'retrato',
        'USER':         'root',
        'PASSWORD':     '',
        'HOST':         'localhost',
        'PORT':         '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_CACHE_DIR, 'data'),
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

INSTALLED_APPS += ('retrato.admin',)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

FACEBOOK_ID = '123456789012345'
