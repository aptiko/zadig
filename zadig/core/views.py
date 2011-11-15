# -*- encoding: utf-8 -*-
import re

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.template import RequestContext
import django.contrib.auth
from django.views.decorators.http import require_POST

from zadig.core import models
from zadig.core.models import PERM_EDIT, entry_types, VObjectMetatags, Language
from zadig.core.utils import split_path, join_path

def _set_languages(request, vobject):
    """Set preferred and effective language."""
    import settings
    request.preferred_language = request.session['language'] \
        if 'language' in request.session else settings.ZADIG_LANGUAGES[0][0]
    request.effective_language = vobject.language.id if vobject.language \
                                                else request.preferred_language

def general_view(request, path):
    # Split the path to path, view_name, parms.
    pathitems = split_path(path)
    path, view_name, parms = '', '', ''
    for i, p in enumerate(pathitems):
        if p.startswith('__') and p.endswith('__'):
            if len(p)<5:
                raise Http404
            view_name = p[2:-2]
            parms = join_path(pathitems[i+1:])
            break
        path = join_path(path, p)
    if request.method=='POST':
        if view_name:
            raise Http404
        view_name = request.POST.get('view_name', '')
        if not view_name:
            raise Http404
    if not view_name: view_name = 'view'
    request.view_name = view_name
    request.parms = parms

    # TODO: probably can _set_languages here and remove it from
    # elsewhere

    # Check if view is one of core views, and return it
    core_views = { 'logout': logout, 'login': login, 'cut': cut, 'paste': paste,
                   'delete': delete }
    if view_name=='view':
        return end_view(request, path)
    elif view_name=='new':
        return new_entry(request, path)
    elif view_name in core_views.keys():
        return core_views[view_name](request, path)

    # Otherwise search for a suitable view
    vobject = models.VObject.objects.get_by_path(path).descendant
    _set_languages(request, vobject)
    if vobject.deletion_mark:
        return vobject.view_deleted()
    method_name = view_name + '_view'
    if hasattr(vobject, method_name):
        return eval('vobject.%s_view()' % (view_name,))
    elif hasattr(vobject.entry.descendant, method_name):
        return eval('vobject.entry.descendant.%s_view()' % (view_name,))
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
    return viewfunc(vobject)

def end_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(path, version_number)\
                                                                .descendant
    _set_languages(request, vobject)
    if vobject.deletion_mark:
        return vobject.view_deleted()
    return vobject.end_view()

def new_entry(request, parent_path):
    parent_vobject = models.VObject.objects.get_by_path(parent_path)
    _set_languages(request, parent_vobject)
    parent_entry = parent_vobject.entry.descendant
    entry_type = request.parms \
            if request.method=='GET' else request.POST.get('entry_type', None)
    class_name = '%sEntry' % (entry_type,)
    new_entry_class = [u for u in entry_types if u.__name__==class_name][0]
    entry = new_entry_class(container=parent_entry)
    return entry.edit_view(new=True)

def logout(request, path):
    django.contrib.auth.logout(request)
    return general_view(request, join_path(path, '__info__'))

class LoginForm(forms.Form):
    from django.contrib.auth.models import User
    username = forms.CharField(max_length=
        django.contrib.auth.models.User._meta.get_field('username').max_length)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

def login(request, path):
    vobject = models.VObject.objects.get_by_path(path)
    if vobject.deletion_mark: raise Http404
    _set_languages(request, vobject)
    message = ''
    if request.user.is_authenticated():
        request.message = _(
                u"You are already logged on; logout to log in again.")
        request.view_name = 'view'
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
                    return HttpResponseRedirect(join_path(path, '__info__'))
                else:
                    raise Exception(_(u"Account is disabled"))
            request.message = _(u"Login incorrect.")
    return render_to_response('login.html',
          { 'vobject': vobject, 'form': form, 'message': message },
                context_instance = RequestContext(request))

@require_POST
def cut(request, path):
    entry = models.Entry.objects.get_by_path(path)
    if entry.vobject.deletion_mark: raise Http404
    request.session['cut_entries'] = [entry.id]
    request.message = _(u"Object has been cut. Will be moved when you "
                        "paste it.")
    request.method = 'GET'
    return general_view(request, join_path(path, '__info__'))

@require_POST
def paste(request, path):
    target_entry = models.Entry.objects.get_by_path(path)
    for entry_id in request.session['cut_entries']:
        e = models.Entry.objects.get(pk=entry_id)
        e.move(target_entry)
    request.session['cut_entries'] = []
    request.method = 'GET'
    return general_view(request, join_path(path, '__contents__'))

@require_POST
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
    return nvobject.view_deleted()
