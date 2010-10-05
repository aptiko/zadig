USE_I18N = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
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

TEMPLATE_DIRS = (ZADIG_PROGRAM_DIR + '/templates',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'south',
    'zadig.core',
    'zadig.zstandard',
    'tinymce',
)

ZADIG_TINYMCE_BLOCKFORMATS = 'p,h1,h2'
ZADIG_TINYMCE_STYLES = 'Float Left=floatLeft,Float Right=floatRight,Align Top=alignTop'
ZADIG_TINYMCE_TABLE_STYLES = 'Plain=plain;Listing=listing;Vertical listing=vertical listing'
