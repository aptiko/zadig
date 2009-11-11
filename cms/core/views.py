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

def _main_buttons(request, selected_view):
    href_prefix = ''
    if re.search(r'__[a-zA-Z]+__/$', request.path): href_prefix = '../'
    result = []
    for x in ('contents', 'view', 'edit', 'history'):
        href_suffix = '__' + x + '__/'
        if x == 'view': href_suffix = ''
        href = href_prefix + href_suffix
        result.append({ 'name': x, 'href': href, 'selected': x==selected_view })
    return result
    
def view_object(request, site, path, version_number=None):
    vobject = stdlib.get_vobject(site, path, version_number)
    if hasattr(vobject, 'page'):
        return render_to_response('view_page.html', { 'vobject': vobject,
                    'main_buttons': _main_buttons(request, 'view')})
    return None

class EditForm(forms.Form):
    # FIXME: metatags should be in many languages
    # FIXME: Get max_lengths from the models
    title = forms.CharField(max_length=150)
    short_title = forms.CharField(max_length=150, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    content = forms.CharField(widget=forms.Textarea)

def edit_entry(request, site, path):
    entry_is_new = False
    try:
        vobject = stdlib.get_vobject(site, path)
        entry = vobject.entry
        language = vobject.language
    except models.Entry.DoesNotExist:
        entry_is_new = True
        entry = stdlib.create_entry(site, path)
        if request.method=='POST':
            entry.save()
            vobject = models.Page(entry=entry, version_number=0,
                language=models.Language.objects.all()[0],
                format=models.ContentFormat.objects.get(descr='rst'),
                content='')
    if request.method!='POST' and entry_is_new:
        form = EditForm()
    elif request.method!='POST' and not entry_is_new:
        form = EditForm({
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
          { 'vobject': vobject, 'form': form,
            'main_buttons': _main_buttons(request, 'edit')})

class MoveItemForm(forms.Form):
    move_object = forms.IntegerField()
    before_object = forms.IntegerField()
    num_of_objects = forms.IntegerField(widget=forms.HiddenInput)
    def clean(self):
        s = self.cleaned_data['move_object']
        t = self.cleaned_data['before_object']
        n = self.cleaned_data['num_of_objects']
        if s<1 or s>n: raise forms.ValidationError(_("The specified object to move is incorrect"))
        if t<1 or t>n+1: raise forms.ValidationError(_("The specified target position is incorrect; use up to one more than the existing number of objects"))
        if s==t or t==s+1: raise forms.ValidationError(_("You can't move an object before itself or before the next one; this would leave it in the same position"))
        return self.cleaned_data

def entry_contents(request, site, path):
    vobject = stdlib.get_vobject(site, path)
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
                { 'vobject': vobject,
                  'move_item_form': move_item_form,
                  'main_buttons': _main_buttons(request, 'contents')})
