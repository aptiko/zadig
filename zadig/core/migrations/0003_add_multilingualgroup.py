
from south.db import db
from django.db import models
from twistycms.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'MultilingualGroup'
        db.create_table('cms_multilingualgroup', (
            ('id', orm['core.multilingualgroup:id']),
        ))
        db.send_create_signal('core', ['MultilingualGroup'])
        
        # Adding field 'Entry.multilingual_group'
        db.add_column('cms_entry', 'multilingual_group', orm['core.entry:multilingual_group'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'MultilingualGroup'
        db.delete_table('cms_multilingualgroup')
        
        # Deleting field 'Entry.multilingual_group'
        db.delete_column('cms_entry', 'multilingual_group_id')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.contentformat': {
            'Meta': {'db_table': "'cms_contentformat'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.entry': {
            'Meta': {'unique_together': "(('container', 'name'), ('container', 'seq'))", 'db_table': "'cms_entry'"},
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
            'Meta': {'unique_together': "(('lentity', 'permission'),)", 'db_table': "'cms_entrypermission'"},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lentity']"}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']"})
        },
        'core.imageentry': {
            'Meta': {'db_table': "'cms_imageentry'"},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.internalredirectionentry': {
            'Meta': {'db_table': "'cms_internalredirectionentry'"},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.language': {
            'Meta': {'db_table': "'cms_language'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '5', 'primary_key': 'True'})
        },
        'core.lentity': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'db_table': "'cms_lentity'"},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'special': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'core.linkentry': {
            'Meta': {'db_table': "'cms_linkentry'"},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.multilingualgroup': {
            'Meta': {'db_table': "'cms_multilingualgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.pageentry': {
            'Meta': {'db_table': "'cms_pageentry'"},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.permission': {
            'Meta': {'db_table': "'cms_permission'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.state': {
            'Meta': {'db_table': "'cms_state'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.statepermission': {
            'Meta': {'unique_together': "(('lentity', 'permission'),)", 'db_table': "'cms_statepermission'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lentity']"}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"})
        },
        'core.statetransition': {
            'Meta': {'unique_together': "(('source_state', 'target_state'),)", 'db_table': "'cms_statetransition'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_rules'", 'to': "orm['core.State']"}),
            'target_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target_rules'", 'to': "orm['core.State']"})
        },
        'core.vimage': {
            'Meta': {'db_table': "'cms_vimage'"},
            'content': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vinternalredirection': {
            'Meta': {'db_table': "'cms_vinternalredirection'"},
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vlink': {
            'Meta': {'db_table': "'cms_vlink'"},
            'target': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.vobject': {
            'Meta': {'unique_together': "(('entry', 'version_number'),)", 'db_table': "'cms_vobject'"},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vobject_set'", 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']", 'null': 'True', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.vobjectmetatags': {
            'Meta': {'unique_together': "(('vobject', 'language'),)", 'db_table': "'cms_vobjectmetatags'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']"}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'vobject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metatags'", 'to': "orm['core.VObject']"})
        },
        'core.vpage': {
            'Meta': {'db_table': "'cms_vpage'"},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ContentFormat']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.workflow': {
            'Meta': {'db_table': "'cms_workflow'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'state_transitions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.StateTransition']"}),
            'states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.State']"})
        }
    }
    
    complete_apps = ['core']
