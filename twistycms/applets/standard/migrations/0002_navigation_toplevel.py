
from south.db import db
from django.db import models
from twistycms.applets.standard.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'EntryOptions.navigation_toplevel'
        db.add_column('standard_entryoptions', 'navigation_toplevel', orm['standard.entryoptions:navigation_toplevel'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'EntryOptions.navigation_toplevel'
        db.delete_column('standard_entryoptions', 'navigation_toplevel')
        
    
    
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
        'core.entry': {
            'Meta': {'unique_together': "(('container', 'name'), ('container', 'seq'))", 'db_table': "'cms_entry'"},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_subentries'", 'null': 'True', 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"})
        },
        'core.state': {
            'Meta': {'db_table': "'cms_state'"},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'standard.entryoptions': {
            'entry': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'}),
            'navigation_toplevel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'no_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }
    
    complete_apps = ['standard']
