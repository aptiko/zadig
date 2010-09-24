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

# Database engine must be one of 'postgresql_psycopg2', 'postgresql',
# 'mysql','sqlite3' or 'oracle'.
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'testdb'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

#TEMPLATE_DIRS.append('/etc/zadig/mycustomtemplates')

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
ZADIG_LANGUAGES = (
    ('en', 'English'),
    ('el', 'Ελληνικά'),
)
WORKFLOW_ID = 1

TINYMCE_JS_URL = ZADIG_MEDIA_URL + 'tinymce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(ZADIG_MEDIA_ROOT, 'tinymce')
