USE_I18N = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'zadig.core.middleware.GeneralMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
)

TEMPLATE_DIRS = (ZADIG_PROGRAM_DIR + '/templates',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.staticfiles',
    'south',
    'zadig.core',
    'zadig.zstandard',
    'tinymce',
)

SITE_ID = 1

STATIC_URL='/__static__/'

SKIP_SOUTH_TESTS = True

ZADIG_TINYMCE_BLOCKFORMATS = 'p,h1,h2'
ZADIG_TINYMCE_STYLES = 'Float Left=floatLeft,Float Right=floatRight,Align Top=alignTop'
ZADIG_TINYMCE_TABLE_STYLES = 'Plain=plain;Listing=listing;Vertical listing=vertical listing'

from datetime import timedelta
ZPAGECOMMENTS_CLOSE_AFTER = timedelta(days=14)

ZBLOG_FROM_EMAIL = 'no-reply@localhost.localdomain'
