"""
Django settings for retrato project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')

STATICFILES_DIRS = [os.path.join(BASE_DIR, "public/static")]

PHOTOS_ROOT_DIR = os.path.join(BASE_DIR, "var/sample/albuns")
BASE_CACHE_DIR = os.path.join(BASE_DIR, "var/cache")
USE_ADMIN = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
#     'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',

    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'retrato.album',
    'retrato.photo',
    'retrato.admin'
)

JASMINE_TEST_DIRECTORY = os.path.join(BASE_DIR, "retrato/album/tests/js")
INSTALLED_APPS += ('django_jasmine', )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'retrato.urls'

WSGI_APPLICATION = 'retrato.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
SECRET_KEY = '1234'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'