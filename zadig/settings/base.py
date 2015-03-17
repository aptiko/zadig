USE_I18N = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'zadig.core',
    'zadig.zstandard',
    'tinymce',
)

SITE_ID = 1
STATIC_URL='/__static__/'
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
ATOMIC_REQUESTS = True

ZADIG_TINYMCE_BLOCKFORMATS = 'p,h1,h2'
ZADIG_TINYMCE_STYLES = 'Float Left=floatLeft,Float Right=floatRight,Align Top=alignTop'
ZADIG_TINYMCE_TABLE_STYLES = 'Plain=plain;Listing=listing;Vertical listing=vertical listing'
