from django.conf.urls.defaults import patterns

urlpatterns = patterns('twistycms.core.views',
    ('^(?P<path>.*)__history__/?$', 'entry_history'),
    ('^(?P<path>.*)__contents__/?$', 'entry_contents'),
    ('^(?P<path>.*)__edit__/?$', 'edit_entry'),
    ('^(?P<path>.*)__state__/(?P<new_state_id>.*)/?$', 'change_state'),
    ('^(?P<parent_path>.*)__newpage__/?$', 'create_new_page'),
    ('^(?P<parent_path>.*)__newimage__/?$', 'create_new_image'),
    ('^(?P<path>.*)__logout__/?$', 'logout'),
    ('^(?P<path>.*)__login__/?$', 'login'),
    ('^(?P<path>.*)$', 'view_object'),
)
