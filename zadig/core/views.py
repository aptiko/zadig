# -*- encoding: utf-8 -*-
import re

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.template import RequestContext
import django.contrib.auth

from zadig.core import models
from zadig.core.models import PERM_EDIT, entry_types, VObjectMetatags, Language

def _set_languages(request, vobject):
    """Set preferred and effective language."""
    import settings
    request.preferred_language = request.session['language'] \
        if 'language' in request.session else settings.ZADIG_LANGUAGES[0][0]
    request.effective_language = vobject.language.id if vobject.language \
                                                else request.preferred_language

def end_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(path, version_number)\
                                                                .descendant
    if vobject.deletion_mark: raise Http404
    _set_languages(request, vobject)
    request.view_name = 'view'
    return vobject.end_view()

def general_view(request, path, view_name, parms):
    vobject = models.VObject.objects.get_by_path(path).descendant
    _set_languages(request, vobject)
    request.view_name = view_name
    if vobject.deletion_mark:
        return vobject.view_deleted(parms)
    method_name = view_name + '_view'
    if hasattr(vobject, method_name):
        return eval('vobject.%s_view(parms=r"%s")' % (view_name, parms))
    elif hasattr(vobject.entry.descendant, method_name):
        return eval('vobject.entry.descendant.%s_view(parms=r"%s")'
                                                        %(view_name, parms))
    # Assume view name is in 'app.viewfuncname' format
    (app, sep, viewfuncname) = view_name.partition('.')
    if not viewfuncname: raise Http404
    try:
        temp = __import__('zadig.%s.views' % (app,), globals(), locals(),
                                                                [viewfuncname])
        viewfunc = temp.__dict__.get(viewfuncname, None)
    except ImportError:
        raise Http404
    if not viewfunc:
        raise Http404
    return viewfunc(vobject, parms=parms)


def new_entry(request, parent_path, entry_type):
    parent_vobject = models.VObject.objects.get_by_path(parent_path)
    _set_languages(request, parent_vobject)
    parent_entry = parent_vobject.entry.descendant
    class_name = '%sEntry' % (entry_type,)
    new_entry_class = [u for u in entry_types if u.__name__==class_name][0]
    entry = new_entry_class(container=parent_entry)
    request.view_name = 'edit'
    return entry.edit_view(new=True)

def logout(request, path):
    django.contrib.auth.logout(request)
    return end_view(request, path)

class LoginForm(forms.Form):
    from django.contrib.auth.models import User
    username = forms.CharField(max_length=
        django.contrib.auth.models.User._meta.get_field('username').max_length)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

def login(request, path):
    vobject = models.VObject.objects.get_by_path(path)
    if vobject.deletion_mark: raise Http404
    request.view_name = 'login'
    _set_languages(request, vobject)
    message = ''
    if request.user.is_authenticated():
        request.message = _(
                u"You are already logged on; logout to log in again.")
        return end_view(request, path)
    elif request.method!='POST':
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
            request.message = _(u"Login incorrect.")
    return render_to_response('login.html',
          { 'vobject': vobject, 'form': form, 'message': message },
                context_instance = RequestContext(request))

def cut(request, path):
    entry = models.Entry.objects.get_by_path(path)
    if entry.vobject.deletion_mark: raise Http404
    request.session['cut_entries'] = [entry.id]
    request.message = _(u"Object has been cut. Will be moved when you "
                        "paste it.")
    return general_view(request, path, 'info', '')

def paste(request, path):
    target_entry = models.Entry.objects.get_by_path(path)
    for entry_id in request.session['cut_entries']:
        e = models.Entry.objects.get(pk=entry_id)
        e.move(target_entry)
    request.session['cut_entries'] = []
    return general_view(request, path, 'contents', '')

def delete(request, path):
    vobject = models.VObject.objects.get_by_path(path).descendant
    if vobject.deletion_mark: raise Http404
    _set_languages(request, vobject)
    if PERM_EDIT not in vobject.entry.permissions:
        raise PermissionDenied(_(u"Permission denied"))
    if not vobject.entry.container:
        raise PermissionDenied(_(u"The root object cannot be deleted"))
    entry = vobject.entry.descendant
    nvobject = entry.vobject_class(entry=entry, version_number =
                                vobject.version_number + 1, deletion_mark=True)
    nvobject.save()
    nmetatags = VObjectMetatags(vobject=nvobject,
        language=Language.get_default(), title=_(u"Deleted"))
    nmetatags.save()
    request.view_name = 'info'
    return nvobject.view_deleted(None)
