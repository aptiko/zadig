from django.conf.urls.defaults import patterns

urlpatterns = patterns('zadig.core.views',
    ('^(?P<path>.*)__history__/?$', 'entry_history'),
    ('^(?P<path>.*)__contents__/?$', 'entry_contents'),
    ('^(?P<path>.*)__edit__/?$', 'edit_entry'),
    ('^(?P<path>.*)__view__/?$', 'info_view'),
    ('^(?P<path>.*)__state__/(?P<new_state_id>[^/]*)/?$', 'change_state'),
    ('^(?P<parent_path>.*)__new__/(?P<entry_type>[^/]*)/?$', 'new_entry'),
    ('^(?P<path>.*)__logout__/?$', 'logout'),
    ('^(?P<path>.*)__login__/?$', 'login'),
    ('^(?P<path>.*)__cut__/?$', 'cut'),
    ('^(?P<path>.*)__paste__/?$', 'paste'),
    ('^(?P<path>.*)__delete__/?$', 'delete'),
    ('^(?P<path>.*)__permissions__/?$', 'entry_permissions'),
    ('^(?P<path>.*)$', 'end_view'),
)
