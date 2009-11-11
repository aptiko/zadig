from django.conf.urls.defaults import *
from django.conf import settings

# Admin
import django.contrib.admin
django.contrib.admin.autodiscover()
urlpatterns = patterns('',
    (r'^__admin__/(.*)', django.contrib.admin.site.root)
)

# Cms
import cms.core.urls
urlpatterns += patterns('',
    (r'^', include('cms.core.urls')),
)

# Static files
if settings.DEBUG:
    import sys
    import os.path
    current_directory = os.path.dirname(sys.modules[__name__].__file__)
    urlpatterns = patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(current_directory, 'static') } )) \
        + urlpatterns
