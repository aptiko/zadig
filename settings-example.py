# Configuration file template for Zadig.
# coding=utf-8

ZADIG_PROGRAM_DIR = '.'

# Leave following three lines as they are, to import several Django settings.
import sys
import os.path
execfile(os.path.join(ZADIG_PROGRAM_DIR, 'settings-base.py'))

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

# Absolute path to the directory that stores binary data.
# See also ZADIG_MEDIA_ROOT below.
MEDIA_ROOT = 'storage/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8$e%+dm&uzb##l-^aa-&t#dlez_i#tsnbttw07cny7go3=ra=y'

# Zadig settings
ZADIG_MEDIA_ROOT = 'static/'         # Directory for JS, CSS, etc.
ZADIG_MEDIA_URL = '/__static__/'
ZADIG_DEFAULT_ROOT_URL = 'http://localhost:8000/'
ZADIG_LANGUAGES = (
    ('en', 'English'),
    ('el', 'Ελληνικά'),
)
WORKFLOW_ID = 1

TINYMCE_JS_URL = ZADIG_MEDIA_URL + 'tinymce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(ZADIG_MEDIA_ROOT, 'tinymce')
