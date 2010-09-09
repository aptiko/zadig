from sys import stderr

from django.dispatch import dispatcher
from django.db.models import signals
from django.contrib.auth.models import User
import settings

from zadig.core import models

def import_initial_data(app, created_models, verbosity, **kwargs):
    if models.Permission in created_models:
        stderr.write("Populating %s table\n" % (models.Permission._meta.db_table,))
        for id, descr in [(models.permissions.VIEW,   "view"),
                          (models.permissions.EDIT,   "edit"),
                          (models.permissions.ADMIN,  "admin"),
                          (models.permissions.DELETE, "delete"),
                          (models.permissions.SEARCH, "search")]:
            new_permission = models.Permission(id=id, descr=descr)
            new_permission.save()
    view   = models.Permission.objects.get(descr="view")
    edit   = models.Permission.objects.get(descr="edit")
    admin  = models.Permission.objects.get(descr="admin")
    delete = models.Permission.objects.get(descr="delete")
    search = models.Permission.objects.get(descr="search")
    if models.Lentity in created_models:
        stderr.write("Populating %s table\n" % (models.Lentity._meta.db_table,))
        for special in (1, 2):
            new_lentity = models.Lentity(special=special)
            new_lentity.save()
        for user in User.objects.all():
            new_user = models.Lentity(user=user)
            new_user.save()
    if models.State in created_models:
        stderr.write("Populating %s table\n" % (models.State._meta.db_table,))
        for descr in ('Nonexistent', 'Private', 'Published'):
            new_state = models.State(descr=descr)
            new_state.save()
    nonexistent = models.State.objects.get(descr='Nonexistent')
    private = models.State.objects.get(descr='Private')
    published = models.State.objects.get(descr='Published')
    if models.StatePermission in created_models:
        stderr.write("Populating %s table\n" % (models.StatePermission._meta.db_table,))
        anonymous_user = models.Lentity.objects.get(special=1)
        logged_on_user = models.Lentity.objects.get(special=2)
        for state, lentity, permission in (
                    (private, logged_on_user, view),
                    (private, logged_on_user, search),
                    (published, anonymous_user, view),
                    (published, anonymous_user, search),):
            new_statepermission = models.StatePermission(state=state,
                    lentity=lentity, permission=permission)
            new_statepermission.save()
    if models.StateTransition in created_models:
        stderr.write("Populating %s table\n" % (models.StateTransition._meta.db_table,))
        for source_state, target_state in ((nonexistent, private),
                    (private, published), (published, private)):
            new_rule = models.StateTransition(source_state=source_state,
                    target_state=target_state)
            new_rule.save()
    if models.Workflow in created_models:
        stderr.write("Populating %s table\n" % (models.Workflow._meta.db_table,))
        new_workflow = models.Workflow(name='Simple publication workflow')
        new_workflow.save()
        new_workflow.states.add(private)
        new_workflow.states.add(published)
        new_workflow.state_transitions.add(models.StateTransition.objects.get(
                                source_state=private, target_state=published))
        new_workflow.state_transitions.add(models.StateTransition .objects.get(
                                source_state=published, target_state=private))
        new_workflow.state_transitions.add(models.StateTransition .objects.get(
                                source_state=nonexistent, target_state=private))
    if models.ContentFormat in created_models:
        stderr.write("Populating %s table\n" % (models.ContentFormat._meta.db_table,))
        new_contentformat = models.ContentFormat(descr='html')
        new_contentformat.save()
        new_contentformat = models.ContentFormat(descr='rst')
        new_contentformat.save()
    if models.Language in created_models:
        stderr.write("Populating %s table\n" % (models.Language._meta.db_table,))
        for lang in settings.LANGUAGES:
            new_language = models.Language(id=lang)
            new_language.save()
    if models.VPage in created_models:
        stderr.write("Creating root page\n")
        entry = models.PageEntry(container=None, name='', seq=1, owner_id=1,
            state=models.Workflow.objects.get(id=settings.WORKFLOW_ID)
                .state_transitions.get(source_state__descr="Nonexistent")
                .target_state)
        entry.save()
        page = models.VPage(entry=entry, version_number=1,
                language_id=settings.LANGUAGES[0],
                format=models.ContentFormat.objects.get(descr='html'),
                content='This is the root page')
        page.save()
        nmetatags = models.VObjectMetatags(vobject=page,
            language_id=settings.LANGUAGES[0], title = 'Welcome',
            short_title='Home', description='Root page.')
        nmetatags.save()
    
signals.post_syncdb.connect(import_initial_data, sender=models)
