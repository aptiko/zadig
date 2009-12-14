# -*- encoding: utf-8 -*-
import re

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _
from cms.core import models
from cms.core import stdlib

def _primary_buttons(request, selected_view):
    href_prefix = ''
    if re.search(r'__[a-zA-Z]+__/$', request.path): href_prefix = '../'
    result = []
    for x in (_(u'contents'), _(u'view'), _(u'edit'), _(u'history')):
        href_suffix = '__' + x + '__/'
        if x == _(u'view'): href_suffix = ''
        href = href_prefix + href_suffix
        result.append({ 'name': x, 'href': href, 'selected': x==selected_view })
    return result

def _secondary_buttons(request):
    result = [
          { 'name': _(u'Add new…'),
            'items': [
                       { 'href': '__newpage__', 'name': _(u'Page') },
                     ]
          },
        ]
    return result
    
def view_object(request, site, path, version_number=None):
    vobject = stdlib.get_vobject(request, site, path, version_number)
    if hasattr(vobject, 'page'):
        return render_to_response('view_page.html', { 'request': request,
                    'vobject': vobject,
                    'primary_buttons': _primary_buttons(request, 'view'),
                    'secondary_buttons': _secondary_buttons(request)})
    return None

class EditForm(forms.Form):
    # FIXME: metatags should be in many languages
    # FIXME: Get max_lengths from the models
    name = forms.CharField(max_length=100)
    title = forms.CharField(max_length=150)
    short_title = forms.CharField(max_length=150, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    content = forms.CharField(widget=forms.Textarea)

def edit_entry(request, site, path):
    # FIXME: form.name ignored
    vobject = stdlib.get_vobject(request, site, path)
    entry = vobject.entry
    language = vobject.language
    if request.method!='POST':
        form = EditForm({
            'name': vobject.entry.name,
            'title': vobject.metatags.default().title,
            'short_title': vobject.metatags.default().short_title,
            'description': vobject.metatags.default().description,
            'content': vobject.page.content
        })
    else:
        form = EditForm(request.POST)
        if form.is_valid():
            npage = models.Page(
                entry=entry,
                version_number=vobject.version_number + 1,
                language=vobject.language,
                format=models.ContentFormat.objects.get(descr='rst'),
                content=form.cleaned_data['content'])
            npage.save()
            nmetatags = models.VObjectMetatags(
                vobject=npage,
                language=vobject.language,
                title=form.cleaned_data['title'],
                short_title=form.cleaned_data['short_title'],
                description=form.cleaned_data['description'])
            nmetatags.save()
            return HttpResponseRedirect(reverse('cms.core.views.view_object',
                                    kwargs={'site':site, 'path': path}))
    return render_to_response('edit_page.html',
          { 'request': request, 'vobject': vobject, 'form': form,
            'primary_buttons': _primary_buttons(request, 'edit'),
            'secondary_buttons': _secondary_buttons(request)})

def create_new_page(request, site, parent_path):
    # FIXME: no language selection, merely gets parent
    # FIXME: only rst, no html
    # FIXME: no check about contents of form.name
    parent_vobject = stdlib.get_vobject(request, site, parent_path)
    if request.method != 'POST':
        form = EditForm()
    else:
        form = EditForm(request.POST)
        if form.is_valid():
            path = parent_path + '/' + form.cleaned_data['name']
            entry = stdlib.create_entry(request, site, path)
            entry.save()
#            vobject = models.Page(entry=entry, version_number=0,
#                language=models.Language.objects.all()[0],
#                format=models.ContentFormat.objects.get(descr='rst'),
#                content='')
            npage = models.Page(
                entry=entry, version_number=1,
                language=parent_vobject.language,
                format=models.ContentFormat.objects.get(descr='rst'),
                content=form.cleaned_data['content'])
            npage.save()
            nmetatags = models.VObjectMetatags(
                vobject=npage, language=parent_vobject.language,
                title=form.cleaned_data['title'],
                short_title=form.cleaned_data['short_title'],
                description=form.cleaned_data['description'])
            nmetatags.save()
            return HttpResponseRedirect(reverse('cms.core.views.view_object',
                                    kwargs={'site':site, 'path': path}))
    return render_to_response('edit_page.html',
        { 'request': request, 'vobject': parent_vobject, 'form': form,
          'primary_buttons': _primary_buttons(request, 'edit'),
          'secondary_buttons': _secondary_buttons(request)})

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

def entry_contents(request, site, path):
    vobject = stdlib.get_vobject(request, site, path)
    if request.method == 'POST':
        move_item_form = MoveItemForm(request.POST)
        if move_item_form.is_valid():
            s = move_item_form.cleaned_data['move_object']
            t = move_item_form.cleaned_data['before_object']
            stdlib.reorder(vobject.entry, s, t)
    else:
        move_item_form = MoveItemForm(initial=
                {'num_of_objects': vobject.entry.subentries.count()})
    return render_to_response('entry_contents.html',
                { 'request': request, 'vobject': vobject,
                  'move_item_form': move_item_form,
                  'primary_buttons': _primary_buttons(request, 'contents'),
                  'secondary_buttons': _secondary_buttons(request)})

def entry_history(request, site, path):
    vobject = stdlib.get_vobject(request, site, path)
    return render_to_response('entry_history.html',
                { 'request': request, 'vobject': vobject,
                  'primary_buttons': _primary_buttons(request, 'history'),
                  'secondary_buttons': _secondary_buttons(request)})
