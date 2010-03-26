from django.conf.urls.defaults import patterns

urlpatterns = patterns('twistycms.core.views',
    ('^(?P<twisty_path>.*/?)__history__/?$', 'entry_history'),
    ('^(?P<twisty_path>.*/?)__contents__/?$', 'entry_contents'),
    ('^(?P<twisty_path>.*/?)__edit__/?$', 'edit_entry'),
    ('^(?P<twisty_path>.*/?)__state__/(?P<new_state_id>.*)/?$', 'change_state'),
    ('^(?P<twisty_path>.*/?)__newpage__/?$', 'create_new_page'),
    ('^(?P<twisty_path>.*/?)__logout__/?$', 'logout'),
    ('^(?P<twisty_path>.*/?)__login__/?$', 'login'),
    ('^(?P<twisty_path>.*/?)$', 'view_object'),
)
