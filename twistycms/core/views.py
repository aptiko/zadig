# -*- encoding: utf-8 -*-
import re

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
import django.contrib.auth

from twistycms.core import models
import twistycms.core
from twistycms.core import utils

# If the following two cannot be deleted, some code reorganizing is unfinished.
from twistycms.core.utils import primary_buttons as _primary_buttons
from twistycms.core.utils import secondary_buttons as _secondary_buttons

def end_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(request, path, version_number)
    return vobject.end_view(request)

def info_view(request, path, version_number=None):
    vobject = models.VObject.objects.get_by_path(request, path, version_number)
    return vobject.info_view(request)

def edit_entry(request, path):
    vobject = models.VObject.objects.get_by_path(request, path)
    entry = vobject.entry.descendant
    return entry.edit_view(request)

def new_entry(request, parent_path, entry_type):
    parent_vobject = models.VObject.objects.get_by_path(request, parent_path)
    parent_entry = parent_vobject.entry.descendant
    new_entry_class = eval('models.%sEntry' % (entry_type,))
    entry = new_entry_class(container=parent_entry)
    return entry.edit_view(request, new=True)

class MoveItemForm(forms.Form):
    move_object = forms.IntegerField()
    before_object = forms.IntegerField()
    num_of_objects = forms.IntegerField(widget=forms.HiddenInput)
    def clean(self):
        s = self.cleaned_data['move_object']
        t = self.cleaned_data['before_object']
        n = self.cleaned_data['num_of_objects']
        if s<1 or s>n:
            raise forms.ValidationError(
                                _("The specified object to move is incorrect"))
        if t<1 or t>n+1:
            raise forms.ValidationError(
                   _("The specified target position is incorrect; "
                    +"use up to one more than the existing number of objects"))
        if s==t or t==s+1:
            raise forms.ValidationError(
             _("You can't move an object before itself or before the next one; "
              +"this would leave it in the same position"))
        return self.cleaned_data

def entry_contents(request, path):
    vobject = models.VObject.objects.get_by_path(request, path)
    subentries = vobject.entry.get_subentries(request)
    if request.method == 'POST':
        move_item_form = MoveItemForm(request.POST)
        if move_item_form.is_valid():
            s = move_item_form.cleaned_data['move_object']
            t = move_item_form.cleaned_data['before_object']
            vobject.entry.reorder(request, s, t)
    else:
        move_item_form = MoveItemForm(initial=
            {'num_of_objects': len(subentries)})
    return render_to_response('entry_contents.html',
            { 'request': request, 'vobject': vobject,
              'subentries': subentries, 'move_item_form': move_item_form,
              'primary_buttons': _primary_buttons(request, vobject, 'contents'),
              'secondary_buttons': _secondary_buttons(request, vobject)})

def entry_history(request, path):
    vobject = models.VObject.objects.get_by_path(request, path)
    return render_to_response('entry_history.html',
            { 'request': request, 'vobject': vobject,
              'primary_buttons': _primary_buttons(request, vobject, 'history'),
              'secondary_buttons': _secondary_buttons(request, vobject)})

def change_state(request, path, new_state_id):
    vobject = models.VObject.objects.get_by_path(request, path)
    entry = vobject.entry
    new_state_id = int(new_state_id)
    if new_state_id not in [x.target_state.id
                            for x in entry.state.source_rules.all()]:
        raise ValidationError(_(u"Invalid target state"))
    entry.state = models.State.objects.get(pk=new_state_id)
    entry.save()
    return HttpResponseRedirect(reverse('twistycms.core.views.end_view',
                kwargs={'path': path }))

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
                    return end_view(request, path)
                else:
                    raise Exception(_(u"Account is disabled"))
            message = _(u"Login incorrect")
    return render_to_response('login.html',
          { 'request': request, 'vobject': vobject, 'form': form,
            'message': message })
