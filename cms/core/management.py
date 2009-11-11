from django.dispatch import dispatcher
from django.db.models import signals
from cms.core import models
from cms.core.stdlib import permissions

def import_initial_data(app, created_models, verbosity, **kwargs):
    if models.Permission in created_models:
        print "Populating %s table" % (models.Permission._meta.db_table,)
        for id, descr in [(permissions.VIEW, "view"),
                    (permissions.EDIT, "edit"), (permissions.ADMIN, "admin"),
                    (permissions.DELETE, "delete")]:
            new_permission = models.Permission(id=id, descr=descr)
            new_permission.save()
    if models.Lentity in created_models:
        print "Populating %s table" % (models.Lentity._meta.db_table,)
        for special in (1, 2):
            new_lentity = models.Lentity(special=special)
            new_lentity.save()
    if models.State in created_models:
        print "Populating %s table" % (models.State._meta.db_table,)
        for descr in ('Private', 'Published'):
            new_state = models.State(descr=descr)
            new_state.save()
    private = models.State.objects.get(descr='Private')
    published = models.State.objects.get(descr='Published')
    if models.StatePermission in created_models:
        print "Populating %s table" % (models.StatePermission._meta.db_table,)
        anonymous_user = models.Lentity.objects.get(special=1)
        logged_on_user = models.Lentity.objects.get(special=2)
        for state, lentity, permission in (
                    (private, logged_on_user, permissions.VIEW),
                    (private, logged_on_user, permissions.SEARCH),
                    (published, anonymous_user, permissions.VIEW),
                    (published, anonymous_user, permissions.SEARCH),):
            new_statepermission = models.StatePermission(state=state,
                    lentity=lentity, permission=permission)
            new_statepermission.save()
    if models.StateTransition in created_models:
        print "Populating %s table" % (models.StateTransition._meta.db_table,)
        for source_state, target_state in (
                    (private, published), (published, private)):
            new_rule = models.StateTransition(source_state=source_state,
                    target_state=target_state)
            new_rule.save()
    if models.Workflow in created_models:
        print "Populating %s table" % (models.Workflow._meta.db_table,)
        new_workflow = models.Workflow(name='Simple publication workflow')
        new_workflow.save()
        new_workflow.states.add(private)
        new_workflow.states.add(published)
        new_workflow.state_transitions.add(models.StateTransition.objects.get(
                                source_state=private, target_state=published))
        new_workflow.state_transitions.add(models.StateTransition .objects.get(
                                source_state=published, target_state=private))
    
signals.post_syncdb.connect(import_initial_data, sender=models)
