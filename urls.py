from django.conf.urls.defaults import *
from django.conf import settings

# Admin
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    (r'^__admin__/(.*)', admin.site.urls)
)

# Cms
import zadig.core.urls
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
    (r'^', include('zadig.core.urls')),
)

# Static files
if settings.DEBUG:
    import sys
    import os.path
    current_directory = os.path.dirname(sys.modules[__name__].__file__)
    zadig_media_url = settings.ZADIG_MEDIA_URL
    # FIXME: The thing below will not work if ZADIG_MEDIA_URL is a full url.
    if zadig_media_url.startswith('/'): zadig_media_url = zadig_media_url[1:]
    if not zadig_media_url.endswith('/'): zadig_media_url += '/'
    urlpatterns = patterns('',
        (r'^%s(?P<path>.*)$' % (zadig_media_url,), 'django.views.static.serve',
            {'document_root': os.path.join(current_directory, 
                                        settings.ZADIG_MEDIA_ROOT) } )) \
        + urlpatterns
