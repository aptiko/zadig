# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BlogEntry'
        db.create_table('zblog_blogentry', (
            ('pageentry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['zstandard.PageEntry'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('zblog', ['BlogEntry'])

        # Adding model 'VBlog'
        db.create_table('zblog_vblog', (
            ('vpage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['zstandard.VPage'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('zblog', ['VBlog'])

        # Adding model 'BlogPostEntry'
        db.create_table('zblog_blogpostentry', (
            ('pageentry_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['zstandard.PageEntry'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('zblog', ['BlogPostEntry'])

        # Adding model 'VBlogPost'
        db.create_table('zblog_vblogpost', (
            ('vpage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['zstandard.VPage'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('zblog', ['VBlogPost'])


    def backwards(self, orm):
        
        # Deleting model 'BlogEntry'
        db.delete_table('zblog_blogentry')

        # Deleting model 'VBlog'
        db.delete_table('zblog_vblog')

        # Deleting model 'BlogPostEntry'
        db.delete_table('zblog_blogpostentry')

        # Deleting model 'VBlogPost'
        db.delete_table('zblog_vblogpost')


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
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vobject_set'", 'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']", 'null': 'True', 'blank': 'True'}),
            'object_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'zblog.blogentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'BlogEntry', '_ormbases': ['zstandard.PageEntry']},
            'pageentry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['zstandard.PageEntry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zblog.blogpostentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'BlogPostEntry', '_ormbases': ['zstandard.PageEntry']},
            'pageentry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['zstandard.PageEntry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zblog.vblog': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VBlog', '_ormbases': ['zstandard.VPage']},
            'vpage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['zstandard.VPage']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zblog.vblogpost': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VBlogPost', '_ormbases': ['zstandard.VPage']},
            'vpage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['zstandard.VPage']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.contentformat': {
            'Meta': {'object_name': 'ContentFormat'},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'zstandard.pageentry': {
            'Meta': {'ordering': "('container__id', 'seq')", 'object_name': 'PageEntry', '_ormbases': ['core.Entry']},
            'entry_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Entry']", 'unique': 'True', 'primary_key': 'True'})
        },
        'zstandard.vpage': {
            'Meta': {'ordering': "('entry', 'version_number')", 'object_name': 'VPage', '_ormbases': ['core.VObject']},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['zstandard.ContentFormat']"}),
            'vobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.VObject']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['zblog']
