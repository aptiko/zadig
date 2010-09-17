# Configuration file template for Zadig.
# coding=utf-8

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

# Leave the following as it is; it imports essential Django settings that are
# expected to be the same in all Zadig installations.
execfile('settings-base.py')
