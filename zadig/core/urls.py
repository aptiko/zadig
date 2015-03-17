from django.conf.urls import patterns

urlpatterns = patterns('zadig.core.views',
    ('^$', 'action_dispatcher'),
    ('^(?P<path>.*)/$', 'action_dispatcher'),
)
