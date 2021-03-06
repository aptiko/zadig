# coding: utf-8

import os

from zadig.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Antonis Christofides', 'anthony@localhost')
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb',
    }
}

#TEMPLATE_DIRS = TEMPLATE_DIRS + ('/etc/zadig/mycustomtemplates',)

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

STATIC_ROOT = 'static/'         # Directory for JS, CSS, etc.
MEDIA_ROOT = 'storage/'         # User-uploaded files

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8$e%+dm&uzb##l-^aa-&t#dlez_i#tsnbttw07cny7go3=ra=y'

# Zadig settings
ZADIG_LANGUAGES = (
    ('en', 'English'),
    ('el', 'Ελληνικά'),
)
ZADIG_WORKFLOW_ID = 1

TINYMCE_JS_URL = STATIC_URL + 'tinymce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'tinymce')
