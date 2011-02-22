from django.conf.urls.defaults import patterns

urlpatterns = patterns('zadig.core.views',
    ('^(?P<parent_path>.*)__new__/(?P<entry_type>[^/]*)/$', 'new_entry'),
    ('^(?P<path>.*)__logout__/$', 'logout'),
    ('^(?P<path>.*)__login__/$', 'login'),
    ('^(?P<path>.*)__cut__/$', 'cut'),
    ('^(?P<path>.*)__paste__/$', 'paste'),
    ('^(?P<path>.*)__delete__/$', 'delete'),
    ('^(?P<path>.*)__(?P<view_name>[^/]+)__/(?P<parms>.*)$', 'general_view'),
    ('^(?P<path>.*)/$', 'end_view'),
    ('^$', 'end_view', {'path': ''} ),
)
