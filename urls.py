from django.conf.urls.defaults import patterns, include

# Admin
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    (r'^__admin__/(.*)', admin.site.urls)
)

# Cms
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
    (r'^', include('zadig.core.urls')),
)

# Static files
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
