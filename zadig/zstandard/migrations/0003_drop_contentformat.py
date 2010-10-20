# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'EntryOptions'
        db.delete_table('zstandard_entryoptions')

        # Deleting model 'ContentFormat'
        db.delete_table('zstandard_contentformat')

        # Adding model 'EntryOptionSet'
        db.create_table('zstandard_entryoptions', (
            ('entry', self.gf('django.db.models.fields.related.OneToOneField')(related_name='ZstandardEntryOptions', unique=True, primary_key=True, to=orm['core.Entry'])),
            ('no_navigation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('no_breadcrumbs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('navigation_toplevel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_author', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('zstandard', ['EntryOptionSet'])

        # Deleting field 'VPage.format'
        db.delete_column('zstandard_vpage', 'format_id')

        # Changing field 'VFile.content'
        db.alter_column('zstandard_vfile', 'content', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True))

        # Changing field 'VImage.content'
        db.alter_column('zstandard_vimage', 'content', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))


    def backwards(self, orm):
        
        # Adding model 'EntryOptions'
        db.create_table('zstandard_entryoptions', (
            ('no_breadcrumbs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('no_navigation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('navigation_toplevel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('entry', self.gf('django.db.models.fields.related.OneToOneField')(related_name='ZstandardEntryOptions', unique=True, primary_key=True, to=orm['core.Entry'])),
            ('show_author', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('zstandard', ['EntryOptions'])

        # Adding model 'ContentFormat'
        db.create_table('zstandard_contentformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('zstandard', ['ContentFormat'])

        # Deleting model 'EntryOptionSet'
        db.delete_table('zstandard_entryoptions')

        # Adding field 'VPage.format'
        db.add_column('zstandard_vpage', 'format', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['zstandard.ContentFormat']), keep_default=False)

        # Changing field 'VFile.content'
        db.alter_column('zstandard_vfile', 'content', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Changing field 'VImage.content'
        db.alter_column('zstandard_vimage', 'content', self.gf('django.db.models.fields.files.ImageField')(max_length=100))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.entry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'unique_together': "(('container', 'name'), ('container', 'seq'))", 'object_name': 'Entry', 'db_table': "'zadig_entry'"},
            'btemplate': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_subentries'", 'null': 'True', 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multilingual_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MultilingualGroup']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"})
        },
        'core.language': {
            'Meta': {'object_name': 'Language', 'db_table': "'zadig_language'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '5', 'primary_key': 'True'})
        },
        'core.multilingualgroup': {
            'Meta': {'object_name': 'MultilingualGroup', 'db_table': "'zadig_multilingualgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.state': {
            'Meta': {'object_name': 'State', 'db_table': "'zadig_state'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.vobject': {
            'Meta': {'ordering': "('entry', 'version_number')", 'unique_together': "(('entry', 'version_number'),)", 'object_name': 'VObject', 'db_table': "'zadig_vobject'"},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deletion_mark': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vobject_set'", 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']", 'null': 'True', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'zstandard.entryoptionset': {
            'Meta': {'object_name': 'EntryOptionSet', 'db_table': "'zstandard_entryoptions'"},
            'entry': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ZstandardEntryOptions'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['core.Entry']"}),
            'navigation_toplevel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_breadcrumbs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_author': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'zstandard.fileentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'FileEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.imageentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'ImageEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.internalredirectionentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'InternalRedirectionEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.linkentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'LinkEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.pageentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'PageEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vfile': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VFile', '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vimage': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VImage', '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vinternalredirection': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VInternalRedirection', '_ormbases': ['core.VObject']},
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vlink': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VLink', '_ormbases': ['core.VObject']},
            'target': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vpage': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VPage', '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['zstandard']
