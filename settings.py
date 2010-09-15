# Django settings for Zadig project.
# coding=utf-8

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Antonis Christofides', 'anthony@localhost')
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql','sqlite3' or 'oracle'.
DATABASE_NAME = 'testdb'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

# Absolute path to the directory that stores binary data.
# See also ZADIG_MEDIA_ROOT below.
MEDIA_ROOT = 'storage/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8$e%+dm&uzb##l-^aa-&t#dlez_i#tsnbttw07cny7go3=ra=y'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'zadig.core.middleware.GeneralMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "zadig.core.context_processors.zadig_media",
)

import sys
import os.path
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'south',
    'zadig.core',
    'zadig.applets.standard',
    'tinymce',
)

# Zadig settings
ZADIG_MEDIA_ROOT = 'static/'         # Directory for JS, CSS, etc.
ZADIG_MEDIA_URL = '/__static__/'
ZADIG_LANGUAGES = (
    ('en', 'English'),
    ('el', 'Ελληνικά'),
)
WORKFLOW_ID = 1

# TinyMCE settings
TINYMCE_JS_URL = ZADIG_MEDIA_URL + 'tinymce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(ZADIG_MEDIA_ROOT, 'tinymce')
