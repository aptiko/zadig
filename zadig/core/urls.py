from django.conf.urls.defaults import patterns

urlpatterns = patterns('zadig.core.views',
    ('^(?P<path>.*)$', 'general_view'),
)
