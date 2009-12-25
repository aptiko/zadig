from django.dispatch import dispatcher
from django.db.models import signals
from cms.core import models
from django.contrib.auth.models import User
from sys import stderr

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
    
signals.post_syncdb.connect(import_initial_data, sender=models)
