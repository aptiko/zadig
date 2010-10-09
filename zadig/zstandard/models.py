import mimetypes

from django.db import models
from django.template import RequestContext
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
import settings

from zadig.core.models import Entry, VObject
from zadig.core import entry_types, entry_option_sets
from zadig.core import utils


### Page ###


class ContentFormat(models.Model):
    descr = models.CharField(max_length=20)

    def __unicode__(self):
        return self.descr


class EditPageForm(forms.Form):
    from tinymce.widgets import TinyMCE
    content = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30},
        mce_attrs={
            'content_css': settings.ZADIG_MEDIA_URL + '/style.css',
            'convert_urls': False,
            'entity_encoding': 'raw',
            'theme': 'advanced',
            'plugins': 'table, inlinepopups,autosave',
            'theme_advanced_blockformats': settings.ZADIG_TINYMCE_BLOCKFORMATS,
            'theme_advanced_styles': settings.ZADIG_TINYMCE_STYLES,
            'table_styles': settings.ZADIG_TINYMCE_TABLE_STYLES,
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_toolbar_align': 'left',
            'theme_advanced_buttons1': 'bold,italic,sup,sub,|,numlist,bullist,outdent,indent,|,image,link,unlink,|,removeformat,code,formatselect,styleselect',
            'theme_advanced_buttons2': 'tablecontrols',
            'theme_advanced_buttons3': '',
            'popup_css': settings.ZADIG_MEDIA_URL + '/tinymce_popup.css',
        }), required=False)

    def render(self):
        return self['content']


class VPage(VObject):
    format = models.ForeignKey(ContentFormat)
    content = models.TextField(blank=True)

    def end_view(self, parms=None):
        return render_to_response('view_page.html', { 'vobject': self },
                context_instance = RequestContext(self.request))

    def info_view(self, parms=None):
        return self.end_view()


class PageEntry(Entry):
    edit_template_name = 'edit_page.html'
    vobject_class = VPage
    typename = _(u"Page")

    def edit_subform(self, data=None, files=None, new=False):
        initial = None if new else {'content': self.vobject.content} 
        return EditPageForm(data=data, files=files, initial=initial)

    def process_edit_subform(self, vobject, form):
        vobject.format=ContentFormat.objects.get(descr='html')
        vobject.content=utils.sanitize_html(form.cleaned_data['content'])


entry_types.append(PageEntry)


### File ###


class VFile(VObject):
    content = models.FileField(upload_to="files")

    def end_view(self, parms=None):
        from django.core.servers.basehttp import FileWrapper
        content_type = mimetypes.guess_type(self.content.path)[0]
        wrapper = FileWrapper(open(self.content.path))
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-length'] = self.content.size
        return response

    def info_view(self, parms=None):
        return render_to_response('view_file.html', { 'vobject': self },
                context_instance = RequestContext(self.request))


class EditFileForm(forms.Form):
    content = forms.FileField()

    def render(self):
        return self.as_table()


class FileEntry(Entry):
    vobject_class = VFile
    typename = _(u"File")

    def edit_subform(self, data=None, files=None, new=False):
        initial = None if new else {'content': self.vobject.content} 
        return EditFileForm(data=data, files=files, initial=initial)

    def process_edit_subform(self, vobject, form):
        vobject.content = form.cleaned_data['content']


entry_types.append(FileEntry)


### Image ###


class VImage(VObject):
    content = models.ImageField(upload_to="images")

    def end_view(self, parms=None):
        from django.core.servers.basehttp import FileWrapper
        content_type = mimetypes.guess_type(self.content.path)[0]
        wrapper = FileWrapper(open(self.content.path))
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-length'] = self.content.size
        return response

    def info_view(self, parms=None):
        return render_to_response('view_image.html', { 'vobject': self },
                context_instance = RequestContext(self.request))

    def resized_view(self, parms="400"):
        import Image
        im = Image.open(self.content.path)
        target_size = int(parms.strip('/'))
        factor = float(target_size)/max(im.size)
        if factor<1.0:
            newsize = [factor*x for x in im.size]
            im = im.resize(newsize, Image.BILINEAR)
        content_type = mimetypes.guess_type(self.content.path)[0]
        response = HttpResponse(content_type=content_type)
        im.save(response, content_type.split('/')[1])
        return response


class EditImageForm(forms.Form):
    content = forms.ImageField()

    def render(self):
        return self.as_table()


class ImageEntry(Entry):
    vobject_class = VImage
    typename = _(u"Image")

    def edit_subform(self, data=None, files=None, new=False):
        initial = None if new else {'content': self.vobject.content} 
        return EditImageForm(data=data, files=files, initial=initial)

    def process_edit_subform(self, vobject, form):
        vobject.content=form.cleaned_data['content']


entry_types.append(ImageEntry)


### Link ###


class VLink(VObject):
    target = models.URLField()

    def end_view(self, parms=None):
        # FIXME: This should not work like this, should directly link outside
        from django.http import HttpResponsePermanentRedirect
        return HttpResponsePermanentRedirect(self.target)

    def info_view(self, parms=None):
        return render_to_response('view_link.html', { 'vobject': self },
                context_instance = RequestContext(self.request))


class EditLinkForm(forms.Form):
    target = forms.URLField()

    def render(self):
        return self.as_table()


class LinkEntry(Entry):
    edit_subform_class = EditLinkForm
    vobject_class = VLink
    typename = _(u"External link")

    def edit_subform(self, data=None, files=None, new=False):
        initial = None if new else {'target': self.vobject.target} 
        return EditLinkForm(data=data, files=files, initial=initial)

    def process_edit_subform(self, vobject, form):
        vobject.target = form.cleaned_data['target']


entry_types.append(LinkEntry)


### InternalRedirection ###

# FIXME: Should subclass link or something


class VInternalRedirection(VObject):
    target = models.ForeignKey(Entry)

    def end_view(self, parms=None):
        from django.http import HttpResponsePermanentRedirect
        return HttpResponsePermanentRedirect(self.target.spath)

    def info_view(self, parms=None):
        return render_to_response('view_internalredirection.html',
                { 'vobject': self },
                context_instance = RequestContext(self.request))


class EditInternalRedirectionForm(forms.Form):
    target = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        EditInternalRedirectionForm.base_fields['target'].choices = [
                                (e.id, e.spath) for e in Entry.objects.all()]
        super(EditInternalRedirectionForm, self).__init__(*args, **kwargs)

    def render(self):
        return self.as_table()


class InternalRedirectionEntry(Entry):
    edit_subform_class = EditInternalRedirectionForm
    vobject_class = VInternalRedirection
    typename = _(u"Internal redirection")

    @classmethod
    def can_create(cls, parent):
        return False

    def edit_subform(self, data=None, files=None, new=False):
        initial = None if new else {'target': self.vobject.target} 
        return EditInternalRedirectionForm(data=data, files=files,
                                                        initial=initial)

    def process_edit_subform(self, vobject, form):
        vobject.target = Entry.objects.get(id=int(form.cleaned_data['target']))


entry_types.append(InternalRedirectionEntry)


### Other ###

class EntryOptionsForm(forms.Form):
    no_breadcrumbs = forms.BooleanField(label=_(u"Don't show in Breadcrumbs"),
                                                    required=False)
    no_navigation = forms.BooleanField(label=_(u"Don't show in Navigation"),
                                                    required=False)
    navigation_toplevel = forms.BooleanField(required=False,
                        label=_(u"Show this page as top level in navigation"))
    show_author = forms.BooleanField(required=False, label=_(u"Show author"))


class EntryOptionSet(models.Model):
    entry = models.OneToOneField(Entry, primary_key=True,
                                    related_name='ZstandardEntryOptions')
    no_navigation = models.BooleanField()
    no_breadcrumbs = models.BooleanField()
    navigation_toplevel = models.BooleanField()
    show_author = models.BooleanField()

    form = EntryOptionsForm

    def get_form_from_data(self):
        return EntryOptionsForm({'no_breadcrumbs': self.no_breadcrumbs,
            'no_navigation': self.no_navigation,
            'navigation_toplevel': self.navigation_toplevel,
            'show_author': self.show_author})

    def set_data_from_form(self, form):
        self.no_breadcrumbs = form.cleaned_data['no_breadcrumbs']
        self.no_navigation = form.cleaned_data['no_navigation']
        self.navigation_toplevel = form.cleaned_data['navigation_toplevel']
        self.show_author = form.cleaned_data['show_author']
        
    class Meta:
        db_table = 'zstandard_entryoptions'

entry_option_sets.append(EntryOptionSet)
