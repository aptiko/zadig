from django.conf.urls.defaults import patterns

urlpatterns = patterns('twistycms.core.views',
    ('^(?P<site>[^/]*)(?P<path>.*)/__history__/$', 'entry_history'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__contents__/$', 'entry_contents'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__edit__/$', 'edit_entry'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__state__/(?P<new_state_id>.*)/$',
                                                            'change_state'),
    ('^(?P<site>[^/]*)(?P<parent_path>.*)/__newpage__/$', 'create_new_page'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__logout__/$', 'logout'),
    ('^(?P<site>[^/]*)(?P<path>.*)/__login__/$', 'login'),
    ('^(?P<site>[^/]*)(?P<path>.*)/$', 'view_object'),
)
