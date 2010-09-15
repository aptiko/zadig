# -*- encoding: utf-8 -*-
import re

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.template import RequestContext
import django.contrib.auth

from zadig.core import models
from zadig.core.models import permissions

def _set_languages(vobject):
    """Set preferred and effective language."""
    import settings
    request = vobject.request
    request.preferred_language = request.session['language'] \
        if 'language' in request.session else settings.ZADIG_LANGUAGES[0][0]
    request.effective_language = vobject.language.id if vobject.language \
                                                else request.preferred_language

def end_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(request, path, version_number)\
                                                                .descendant
    _set_languages(vobject)
    vobject.request.view_name = _(u'view')
    return vobject.end_view()

def info_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(request, path, version_number)\
                                                                .descendant
    _set_languages(vobject)
    vobject.request.view_name = _(u'view')
    return vobject.info_view()

def edit_entry(request, path):
    entry = models.Entry.objects.get_by_path(request, path).descendant
    _set_languages(entry.vobject)
    entry.request.view_name = _(u'edit')
    return entry.edit_view()

def new_entry(request, parent_path, entry_type):
    parent_vobject = models.VObject.objects.get_by_path(request, parent_path)
    _set_languages(parent_vobject)
    parent_entry = parent_vobject.entry.descendant
    new_entry_class = eval('models.%sEntry' % (entry_type,))
    entry = new_entry_class(container=parent_entry)
    entry.request = request
    entry.request.view_name = _(u'edit')
    return entry.edit_view(new=True)

def entry_contents(request, path):
    entry = models.Entry.objects.get_by_path(request, path)
    _set_languages(entry.vobject)
    entry.request.view_name = _(u'contents')
    return entry.contents_view()

def entry_history(request, path):
    entry = models.Entry.objects.get_by_path(request, path)
    _set_languages(entry.vobject)
    entry.request.view_name = _(u'history')
    return entry.history_view()

def entry_permissions(request, path):
    entry = models.Entry.objects.get_by_path(request, path)
    _set_languages(entry.vobject)
    entry.request.view_name = _(u'permissions')
    return entry.permissions_view()

def change_state(request, path, new_state_id):
    vobject = models.VObject.objects.get_by_path(request, path)
    entry = vobject.entry
    new_state_id = int(new_state_id)
    if new_state_id not in [x.target_state.id
                            for x in entry.state.source_rules.all()]:
        raise ValidationError(_(u"Invalid target state"))
    entry.state = models.State.objects.get(pk=new_state_id)
    entry.save()
    return HttpResponseRedirect(entry.spath)

def logout(request, path):
    django.contrib.auth.logout(request)
    return end_view(request, path)

class LoginForm(forms.Form):
    from django.contrib.auth.models import User
    username = forms.CharField(max_length=
        django.contrib.auth.models.User._meta.get_field('username').max_length)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

def login(request, path):
    vobject = models.VObject.objects.get_by_path(request, path)
    _set_languages(vobject)
    message = ''
    if request.method!='POST':
        form = LoginForm()
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = django.contrib.auth.authenticate(
                            username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    django.contrib.auth.login(request, user)
                    models.Lentity.objects.get_or_create(user=user)
                    return end_view(request, path)
                else:
                    raise Exception(_(u"Account is disabled"))
            message = _(u"Login incorrect")
    return render_to_response('login.html',
          { 'vobject': vobject, 'form': form, 'message': message },
                context_instance = RequestContext(request))

def cut(request, path):
    entry = models.Entry.objects.get_by_path(request, path)
    request.session['cut_entries'] = [entry.id]
    return info_view(request, path)

def paste(request, path):
    target_entry = models.Entry.objects.get_by_path(request, path)
    for entry_id in request.session['cut_entries']:
        e = models.Entry.objects.get(pk=entry_id)
        e.request = request
        e.move(target_entry)
    request.session['cut_entries'] = []
    return entry_contents(request, path)

def delete(request, path):
    vobject = models.VObject.objects.get_by_path(request, path)
    _set_languages(vobject)
    if permissions.DELETE not in vobject.rentry.permissions:
        raise PermissionDenied(_(u"Permission denied"))
    if not vobject.rentry.rcontainer:
        raise PermissionDenied(_(u"The root object cannot be deleted"))
    if request.method=='POST' and 'confirm' in request.POST and \
                                            request.POST['confirm']:
        container  = vobject.rentry.rcontainer
        vobject.rentry.delete()
        return entry_contents(request, container.path)
    elif request.method=='POST':
        return info_view(request, path)
    else:
        return render_to_response('delete_entry.html', 
                { 'vobject': vobject },
                context_instance = RequestContext(request))
