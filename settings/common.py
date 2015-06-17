# Django settings for thewulf project.
from __future__ import absolute_import, print_function

import os
from . import DBNAME, ENV


local_development = ENV == "local"

DEBUG = local_development
TEMPLATE_DEBUG = DEBUG
LIVE_DEV = os.environ.get("LIVEDEV", False)

ALLOWED_HOSTS = [
    ".thewulf.org"
]

ADMINS = (
  ('mwinter', 'mwinter@thewulf.org'),
  ('scott', 'scottcazan@gmail.com'),
  ('ayoung', 'ayoung@thewulf.org')
)
MANAGERS = ADMINS

PROJECT_ROOT = os.path.split(os.path.dirname(__file__))[0]
SECRET_KEY = os.environ.get("SECRETS", "d0nt-3@t-my-1c3-cr3@m")

dbhost = '' if local_development else 'thewulfdb.thewulf.org'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DBNAME,
        'USER': 'thewulf',
        'PASSWORD': os.environ.get("DBPASS", ''),
        'HOST': dbhost
    }
}

ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"
GRAPPELLI_ADMIN_TITLE = 'the wulf. administration'
GRAPPELLI_INDEX_DASHBOARD = 'thewulf.dashboard.CustomIndexDashboard'

ROOT_URLCONF = "thewulf.urls"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL = "/media/" if local_development else "http://media.thewulf.org/media/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = "/static/" if local_development else "http://media.thewulf.org/static/"

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles'
)
THIRD_PARTY_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',  # necessary hack...
    'south'
)
LOCAL_APPS = (
    'apps.thewulfcms',
    'apps.django_monitor'  # seriously ?!??!?!?
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = True

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    'django.contrib.messages.context_processors.messages'
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json'
}
