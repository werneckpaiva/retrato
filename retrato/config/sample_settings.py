from retrato.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PHOTOS_ROOT_DIR = '/meus_arquivos/photos/'

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
        'LOCATION': os.path.join(BASE_DIR, "var/cache/data"),
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'
