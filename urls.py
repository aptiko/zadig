from django.conf.urls import patterns, include

# Admin
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    (r'^__admin__/', admin.site.urls)
)

# Static files
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

# Cms
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
    (r'^', include('zadig.core.urls')),
)
