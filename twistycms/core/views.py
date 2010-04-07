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
from tinymce.widgets import TinyMCE

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

class EditForm(forms.Form):
    # FIXME: metatags should be in many languages
    language = forms.ChoiceField(choices=
        [(l.id, l.id) for l in models.Language.objects.all()])
    name = forms.CharField(required=False,
        max_length=models.Entry._meta.get_field('name').max_length)
    title = forms.CharField(
        max_length=models.VObjectMetatags._meta.get_field('title').max_length)
    short_title = forms.CharField(required=False, max_length=
        models.VObjectMetatags._meta.get_field('short_title').max_length)
    description = forms.CharField(widget=forms.Textarea, required=False)
    content = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30},
        mce_attrs={
            'content_css': '/static/style.css',
            'convert_urls': False,
            'theme': 'advanced',
            'theme_advanced_blockformats': 'p,h1,h2',
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_toolbar_align': 'left',
            'theme_advanced_buttons1': 'bold,italic,justifyleft,justifycenter,justifyright,numlist,bullist,outdent,indent,removeformat,image,link,unlink,anchor,code,formatselect',
            'theme_advanced_buttons2': '',
            'theme_advanced_buttons3': '',
        }), required=False)

class ImageForm(forms.Form):
    # FIXME: metatags should be in many languages
    language = forms.ChoiceField(choices=
        [(l.id, l.id) for l in models.Language.objects.all()])
    name = forms.CharField(required=False,
        max_length=models.Entry._meta.get_field('name').max_length)
    title = forms.CharField(
        max_length=models.VObjectMetatags._meta.get_field('title').max_length)
    short_title = forms.CharField(required=False, max_length=
        models.VObjectMetatags._meta.get_field('short_title').max_length)
    description = forms.CharField(widget=forms.Textarea, required=False)
    content = forms.ImageField()

def edit_entry(request, path):
    # FIXME: form.name ignored
    vobject = models.VObject.objects.get_by_path(request, path)
    entry = vobject.entry
    language = vobject.language
    applet_options = [o for o in twistycms.core.applet_options if o['entry_options']]
    if request.method!='POST':
        form = EditForm({
            'language': vobject.language.id,
            'name': vobject.entry.name,
            'title': vobject.metatags.default().title,
            'short_title': vobject.metatags.default().short_title,
            'description': vobject.metatags.default().description,
            'content': vobject.page.content
        })
        for o in applet_options:
            o['entry_options_form'] = o['entry_options'](request, path)
    else:
        form = EditForm(request.POST)
        for o in applet_options:
            o['entry_options_form'] = o['EntryOptionsForm'](request.POST)
        all_forms_are_valid = all((form.is_valid(),) +
            tuple([o['entry_options_form'].is_valid() for o in applet_options]))
        if all_forms_are_valid:
            npage = models.Page(
                entry=entry,
                version_number=vobject.version_number + 1,
                language=models.Language.objects.get(
                                            id=form.cleaned_data['language']),
                format=models.ContentFormat.objects.get(descr='html'),
                content=utils.sanitize_html(form.cleaned_data['content']))
            npage.save()
            nmetatags = models.VObjectMetatags(
                vobject=npage,
                language=npage.language,
                title=form.cleaned_data['title'],
                short_title=form.cleaned_data['short_title'],
                description=form.cleaned_data['description'])
            nmetatags.save()
            for o in applet_options:
                o['entry_options'](request, path, o['entry_options_form'])
            return HttpResponseRedirect(reverse('twistycms.core.views.end_view',
                        kwargs={'path': path }))
    return render_to_response('edit_page.html',
          { 'request': request, 'vobject': vobject, 'form': form,
            'applet_options': applet_options,
            'primary_buttons': _primary_buttons(request, vobject, 'edit'),
            'secondary_buttons': _secondary_buttons(request, vobject)})

def create_new_page(request, parent_path):
    # FIXME: only html, no rst
    # FIXME: no check about contents of form.name
    parent_vobject = models.VObject.objects.get_by_path(request, parent_path)
    if request.method != 'POST':
        form = EditForm({ 'language': parent_vobject.language.id })
    else:
        form = EditForm(request.POST)
        if form.is_valid():
            path = parent_path + '/' + form.cleaned_data['name']
            entry = models.Entry(request, path)
            entry.save()
            npage = models.Page(
                entry=entry, version_number=1,
                language=models.Language.objects.get(
                                            id=form.cleaned_data['language']),
                format=models.ContentFormat.objects.get(descr='html'),
                content=utils.sanitize_html(form.cleaned_data['content']))
            npage.save()
            nmetatags = models.VObjectMetatags(
                vobject=npage,
                language=models.Language.objects.get(
                                            id=form.cleaned_data['language']),
                title=form.cleaned_data['title'],
                short_title=form.cleaned_data['short_title'],
                description=form.cleaned_data['description'])
            nmetatags.save()
            return HttpResponseRedirect(reverse('twistycms.core.views.view_object',
                        kwargs={'path': path }))
    return render_to_response('edit_page.html',
        { 'request': request, 'vobject': parent_vobject, 'form': form,
          'primary_buttons': _primary_buttons(request, parent_vobject, 'edit'),
          'secondary_buttons': _secondary_buttons(request, parent_vobject)})

def create_new_image(request, parent_path):
    parent_vobject = models.VObject.objects.get_by_path(request, parent_path)
    if request.method != 'POST':
        form = ImageForm({ 'language': parent_vobject.language.id })
    else:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            path = parent_path + '/' + form.cleaned_data['name']
            entry = models.Entry(request, path)
            entry.save()
            nimage = models.Image( entry=entry, version_number=1,
                language=models.Language.objects.get(
                                            id=form.cleaned_data['language']),
                content=form.cleaned_data['content'])
            nimage.save()
            nmetatags = models.VObjectMetatags(
                vobject=nimage,
                language=models.Language.objects.get(
                                            id=form.cleaned_data['language']),
                title=form.cleaned_data['title'],
                short_title=form.cleaned_data['short_title'],
                description=form.cleaned_data['description'])
            nmetatags.save()
            return HttpResponseRedirect(reverse('twistycms.core.views.end_view',
                        kwargs={'path': path }))
    return render_to_response('edit_image.html',
        { 'request': request, 'vobject': parent_vobject, 'form': form,
          'primary_buttons': _primary_buttons(request, parent_vobject, 'edit'),
          'secondary_buttons': _secondary_buttons(request, parent_vobject)})
    
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
        form = LoginForm({})
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
