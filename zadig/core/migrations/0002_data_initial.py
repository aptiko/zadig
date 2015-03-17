# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

from zadig.core.models import (EVERYONE, LOGGED_ON_USER, OWNER, PERM_VIEW,
                               PERM_EDIT, PERM_ADMIN, PERM_DELETE, PERM_SEARCH)


def initial_data(apps, schema_editor):
    # Permissions
    Permission = apps.get_model('core', 'Permission')
    for id, descr in [(PERM_VIEW,   "view"),
                      (PERM_EDIT,   "edit"),
                      (PERM_ADMIN,  "admin"),
                      (PERM_DELETE, "delete"),
                      (PERM_SEARCH, "search")]:
        new_permission = Permission(id=id, descr=descr)
        new_permission.save()
    view = Permission.objects.get(descr="view")
    search = Permission.objects.get(descr="search")

    # Lentity
    Lentity = apps.get_model('core', 'Lentity')
    for special in (EVERYONE, LOGGED_ON_USER, OWNER):
        new_lentity = Lentity(special=special)
        new_lentity.save()
    User = apps.get_model('auth', 'User')
    for user in User.objects.all():
        new_user = Lentity(user_id=user.id)
        new_user.save()

    # State
    State = apps.get_model('core', 'State')
    for descr in ('Nonexistent', 'Private', 'Published'):
        new_state = State(descr=descr)
        new_state.save()
    nonexistent = State.objects.get(descr='Nonexistent')
    private = State.objects.get(descr='Private')
    published = State.objects.get(descr='Published')

    # StatePermission
    StatePermission = apps.get_model('core', 'StatePermission')
    everyone = Lentity.objects.get(special=EVERYONE)
    logged_on_user = Lentity.objects.get(special=LOGGED_ON_USER)
    for state, lentity, permission in (
            (private, logged_on_user, view),
            (private, logged_on_user, search),
            (published, everyone, view),
            (published, everyone, search),):
        new_statepermission = StatePermission(
            state=state, lentity=lentity, permission=permission)
        new_statepermission.save()

    # StateTransition
    StateTransition = apps.get_model('core', 'StateTransition')
    for source_state, target_state in ((nonexistent, private),
                                       (private, published),
                                       (published, private)):
        new_rule = StateTransition(source_state=source_state,
                                   target_state=target_state,
                                   lentity=Lentity.objects.get(special=OWNER))
        new_rule.save()

    # Workflow
    Workflow = apps.get_model('core', 'Workflow')
    new_workflow = Workflow(name='Simple publication workflow')
    new_workflow.save()
    new_workflow.states.add(private)
    new_workflow.states.add(published)
    new_workflow.state_transitions.add(
        StateTransition.objects.get(source_state=private,
                                    target_state=published))
    new_workflow.state_transitions.add(
        StateTransition.objects.get(source_state=published,
                                    target_state=private))
    new_workflow.state_transitions.add(
        StateTransition.objects.get(source_state=nonexistent,
                                    target_state=private))

    # Language
    Language = apps.get_model('core', 'Language')
    for lang_id, lang_descr in settings.ZADIG_LANGUAGES:
        new_language = Language(id=lang_id, descr=lang_descr)
        new_language.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
