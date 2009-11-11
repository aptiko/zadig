from django.conf.urls.defaults import patterns

urlpatterns = patterns('cms.core.views',
    ('^(?P<site>[^/]*)(?P<path>.*)/__contents__/$', 'entry_contents'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__edit__/$', 'edit_entry'),
    ('^(?P<site>[^/]*)(?P<path>.*)/$', 'view_object'),
)
