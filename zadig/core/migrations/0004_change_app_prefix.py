# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

_tables = ('language', 'permission', 'lentity', 'state', 'statepermission',
          'statetransition', 'workflow', 'multilingualgroup', 'entry',
          'entrypermission', 'vobject', 'vobjectmetatags', 'contentformat',
          'pageentry', 'vpage', 'imageentry', 'vimage', 'linkentry', 'vlink',
          'internalredirectionentry', 'vinternalredirection',
          'workflow_states', 'workflow_state_transitions')

class Migration(SchemaMigration):

    def forwards(self, orm):
        for t in _tables:
            db.rename_table('cms_'+t, 'zadig_'+t)

    def backwards(self, orm):
        for t in _tables:
            db.rename_table('zadig_'+t, 'cms_'+t)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.contentformat': {
            'Meta': {'object_name': 'ContentFormat', 'db_table': "'zadig_contentformat'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.entry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'unique_together': "(('container', 'name'), ('container', 'seq'))", 'object_name': 'Entry', 'db_table': "'zadig_entry'"},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_subentries'", 'null': 'True', 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multilingual_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MultilingualGroup']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"})
        },
        'core.entrypermission': {
            'Meta': {'unique_together': "(('lentity', 'permission'),)", 'object_name': 'EntryPermission', 'db_table': "'zadig_entrypermission'"},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lentity']"}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']"})
        },
        'core.imageentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'ImageEntry', 'db_table': "'zadig_imageentry'", '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.internalredirectionentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'InternalRedirectionEntry', 'db_table': "'zadig_internalredirectionentry'", '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.language': {
            'Meta': {'object_name': 'Language', 'db_table': "'zadig_language'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '5', 'primary_key': 'True'})
        },
        'core.lentity': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'object_name': 'Lentity', 'db_table': "'zadig_lentity'"},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'special': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'core.linkentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'LinkEntry', 'db_table': "'zadig_linkentry'", '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.multilingualgroup': {
            'Meta': {'object_name': 'MultilingualGroup', 'db_table': "'zadig_multilingualgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.pageentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'PageEntry', 'db_table': "'zadig_pageentry'", '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.permission': {
            'Meta': {'object_name': 'Permission', 'db_table': "'zadig_permission'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.state': {
            'Meta': {'object_name': 'State', 'db_table': "'zadig_state'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.statepermission': {
            'Meta': {'unique_together': "(('lentity', 'permission'),)", 'object_name': 'StatePermission', 'db_table': "'zadig_statepermission'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lentity']"}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"})
        },
        'core.statetransition': {
            'Meta': {'unique_together': "(('source_state', 'target_state'),)", 'object_name': 'StateTransition', 'db_table': "'zadig_statetransition'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_rules'", 'to': "orm['core.State']"}),
            'target_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target_rules'", 'to': "orm['core.State']"})
        },
        'core.vimage': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VImage', 'db_table': "'zadig_vimage'", '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vinternalredirection': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VInternalRedirection', 'db_table': "'zadig_vinternalredirection'", '_ormbases': ['core.VObject']},
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vlink': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VLink', 'db_table': "'zadig_vlink'", '_ormbases': ['core.VObject']},
            'target': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vobject': {
            'Meta': {'ordering': "('entry', 'version_number')", 'unique_together': "(('entry', 'version_number'),)", 'object_name': 'VObject', 'db_table': "'zadig_vobject'"},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vobject_set'", 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']", 'null': 'True', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.vobjectmetatags': {
            'Meta': {'unique_together': "(('vobject', 'language'),)", 'object_name': 'VObjectMetatags', 'db_table': "'zadig_vobjectmetatags'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']"}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'vobject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metatags_set'", 'to': "orm['core.VObject']"})
        },
        'core.vpage': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VPage', 'db_table': "'zadig_vpage'", '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ContentFormat']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.workflow': {
            'Meta': {'object_name': 'Workflow', 'db_table': "'zadig_workflow'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'state_transitions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.StateTransition']"}),
            'states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.State']"})
        }
    }

    complete_apps = ['core']
