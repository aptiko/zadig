from django.conf.urls.defaults import patterns

urlpatterns = patterns('zadig.core.views',
    ('^$', 'action_dispatcher'),
    ('^(?P<path>.*)/$', 'action_dispatcher'),
)
