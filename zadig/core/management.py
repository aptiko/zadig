from sys import stderr

from django.dispatch import dispatcher
from django.db.models import signals
from django.contrib.auth.models import User
import settings

from zadig.core.models import permissions, Permission, Lentity, Language, \
                              ANONYMOUS_USER, LOGGED_ON_USER, State, Workflow, \
                              StatePermission, StateTransition, VObjectMetatags
from zadig.zstandard.models import VPage, PageEntry

def import_initial_data(app, created_models, verbosity, **kwargs):
    if Permission in created_models:
        stderr.write("Populating %s table\n" % (Permission._meta.db_table,))
        for id, descr in [(permissions.VIEW,   "view"),
                          (permissions.EDIT,   "edit"),
                          (permissions.ADMIN,  "admin"),
                          (permissions.DELETE, "delete"),
                          (permissions.SEARCH, "search")]:
            new_permission = Permission(id=id, descr=descr)
            new_permission.save()
    view   = Permission.objects.get(descr="view")
    edit   = Permission.objects.get(descr="edit")
    admin  = Permission.objects.get(descr="admin")
    delete = Permission.objects.get(descr="delete")
    search = Permission.objects.get(descr="search")
    if Lentity in created_models:
        stderr.write("Populating %s table\n" % (Lentity._meta.db_table,))
        for special in (ANONYMOUS_USER, LOGGED_ON_USER):
            new_lentity = Lentity(special=special)
            new_lentity.save()
        for user in User.objects.all():
            new_user = Lentity(user=user)
            new_user.save()
    if State in created_models:
        stderr.write("Populating %s table\n" % (State._meta.db_table,))
        for descr in ('Nonexistent', 'Private', 'Published'):
            new_state = State(descr=descr)
            new_state.save()
    nonexistent = State.objects.get(descr='Nonexistent')
    private = State.objects.get(descr='Private')
    published = State.objects.get(descr='Published')
    if StatePermission in created_models:
        stderr.write("Populating %s table\n" % (StatePermission._meta.db_table,))
        anonymous_user = Lentity.objects.get(special=ANONYMOUS_USER)
        logged_on_user = Lentity.objects.get(special=LOGGED_ON_USER)
        for state, lentity, permission in (
                    (private, logged_on_user, view),
                    (private, logged_on_user, search),
                    (published, anonymous_user, view),
                    (published, anonymous_user, search),):
            new_statepermission = StatePermission(state=state,
                    lentity=lentity, permission=permission)
            new_statepermission.save()
    if StateTransition in created_models:
        stderr.write("Populating %s table\n" % (StateTransition._meta.db_table,))
        for source_state, target_state in ((nonexistent, private),
                    (private, published), (published, private)):
            new_rule = StateTransition(source_state=source_state,
                    target_state=target_state)
            new_rule.save()
    if Workflow in created_models:
        stderr.write("Populating %s table\n" % (Workflow._meta.db_table,))
        new_workflow = Workflow(name='Simple publication workflow')
        new_workflow.save()
        new_workflow.states.add(private)
        new_workflow.states.add(published)
        new_workflow.state_transitions.add(StateTransition.objects.get(
                                source_state=private, target_state=published))
        new_workflow.state_transitions.add(StateTransition .objects.get(
                                source_state=published, target_state=private))
        new_workflow.state_transitions.add(StateTransition.objects.get(
                                source_state=nonexistent, target_state=private))
    if Language in created_models:
        stderr.write("Populating %s table\n" % (Language._meta.db_table,))
        for lang_id, lang_descr in settings.ZADIG_LANGUAGES:
            new_language = Language(id=lang_id, descr=lang_descr)
            new_language.save()
    if VPage in created_models:
        stderr.write("Creating root page\n")
        entry = PageEntry(container=None, name='', seq=1, owner_id=1,
            state=Workflow.objects.get(id=settings.WORKFLOW_ID)
                .state_transitions.get(source_state__descr="Nonexistent")
                .target_state)
        entry.save()
        page = VPage(entry=entry, version_number=1,
                language_id=settings.ZADIG_LANGUAGES[0][0],
                content='This is the root page')
        page.save()
        nmetatags = VObjectMetatags(vobject=page,
            language_id=settings.ZADIG_LANGUAGES[0][0], title = 'Welcome',
            short_title='Home', description='Root page.')
        nmetatags.save()
    
import zadig.core.models
signals.post_syncdb.connect(import_initial_data, sender=zadig.core.models)
