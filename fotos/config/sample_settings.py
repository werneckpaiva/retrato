from fotos.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.mysql',
        'NAME':         'fotos',
        'USER':         'root',
        'PASSWORD':     '',
        'HOST':         'localhost',
        'PORT':         '',
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

PHOTOS_ROOT_DIR = os.path.join(BASE_DIR, "../album")
PHOTOS_CACHE_DIR = '/tmp/album/cache/'
