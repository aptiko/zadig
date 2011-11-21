from django.conf.urls.defaults import patterns

urlpatterns = patterns('zadig.core.views',
    ('^(?P<path>.*)$', 'action_dispatcher'),
)
