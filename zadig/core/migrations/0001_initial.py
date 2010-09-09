
from south.db import db
from django.db import models
from twistycms.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Permission'
        db.create_table('cms_permission', (
            ('id', orm['core.Permission:id']),
            ('descr', orm['core.Permission:descr']),
        ))
        db.send_create_signal('core', ['Permission'])
        
        # Adding model 'Entry'
        db.create_table('cms_entry', (
            ('id', orm['core.Entry:id']),
            ('object_class', orm['core.Entry:object_class']),
            ('container', orm['core.Entry:container']),
            ('name', orm['core.Entry:name']),
            ('seq', orm['core.Entry:seq']),
            ('owner', orm['core.Entry:owner']),
            ('state', orm['core.Entry:state']),
        ))
        db.send_create_signal('core', ['Entry'])
        
        # Adding model 'VPage'
        db.create_table('cms_vpage', (
            ('vobject_ptr', orm['core.VPage:vobject_ptr']),
            ('format', orm['core.VPage:format']),
            ('content', orm['core.VPage:content']),
        ))
        db.send_create_signal('core', ['VPage'])
        
        # Adding model 'VImage'
        db.create_table('cms_vimage', (
            ('vobject_ptr', orm['core.VImage:vobject_ptr']),
            ('content', orm['core.VImage:content']),
        ))
        db.send_create_signal('core', ['VImage'])
        
        # Adding model 'VObject'
        db.create_table('cms_vobject', (
            ('id', orm['core.VObject:id']),
            ('object_class', orm['core.VObject:object_class']),
            ('entry', orm['core.VObject:entry']),
            ('version_number', orm['core.VObject:version_number']),
            ('date', orm['core.VObject:date']),
            ('language', orm['core.VObject:language']),
        ))
        db.send_create_signal('core', ['VObject'])
        
        # Adding model 'VLink'
        db.create_table('cms_vlink', (
            ('vobject_ptr', orm['core.VLink:vobject_ptr']),
            ('target', orm['core.VLink:target']),
        ))
        db.send_create_signal('core', ['VLink'])
        
        # Adding model 'Language'
        db.create_table('cms_language', (
            ('id', orm['core.Language:id']),
        ))
        db.send_create_signal('core', ['Language'])
        
        # Adding model 'StatePermission'
        db.create_table('cms_statepermission', (
            ('id', orm['core.StatePermission:id']),
            ('state', orm['core.StatePermission:state']),
            ('lentity', orm['core.StatePermission:lentity']),
            ('permission', orm['core.StatePermission:permission']),
        ))
        db.send_create_signal('core', ['StatePermission'])
        
        # Adding model 'StateTransition'
        db.create_table('cms_statetransition', (
            ('id', orm['core.StateTransition:id']),
            ('source_state', orm['core.StateTransition:source_state']),
            ('target_state', orm['core.StateTransition:target_state']),
        ))
        db.send_create_signal('core', ['StateTransition'])
        
        # Adding model 'Workflow'
        db.create_table('cms_workflow', (
            ('id', orm['core.Workflow:id']),
            ('name', orm['core.Workflow:name']),
        ))
        db.send_create_signal('core', ['Workflow'])
        
        # Adding model 'LinkEntry'
        db.create_table('cms_linkentry', (
            ('entry_ptr', orm['core.LinkEntry:entry_ptr']),
        ))
        db.send_create_signal('core', ['LinkEntry'])
        
        # Adding model 'State'
        db.create_table('cms_state', (
            ('id', orm['core.State:id']),
            ('descr', orm['core.State:descr']),
        ))
        db.send_create_signal('core', ['State'])
        
        # Adding model 'EntryPermission'
        db.create_table('cms_entrypermission', (
            ('id', orm['core.EntryPermission:id']),
            ('entry', orm['core.EntryPermission:entry']),
            ('lentity', orm['core.EntryPermission:lentity']),
            ('permission', orm['core.EntryPermission:permission']),
        ))
        db.send_create_signal('core', ['EntryPermission'])
        
        # Adding model 'VObjectMetatags'
        db.create_table('cms_vobjectmetatags', (
            ('id', orm['core.VObjectMetatags:id']),
            ('vobject', orm['core.VObjectMetatags:vobject']),
            ('language', orm['core.VObjectMetatags:language']),
            ('title', orm['core.VObjectMetatags:title']),
            ('short_title', orm['core.VObjectMetatags:short_title']),
            ('description', orm['core.VObjectMetatags:description']),
        ))
        db.send_create_signal('core', ['VObjectMetatags'])
        
        # Adding model 'InternalRedirectionEntry'
        db.create_table('cms_internalredirectionentry', (
            ('entry_ptr', orm['core.InternalRedirectionEntry:entry_ptr']),
        ))
        db.send_create_signal('core', ['InternalRedirectionEntry'])
        
        # Adding model 'PageEntry'
        db.create_table('cms_pageentry', (
            ('entry_ptr', orm['core.PageEntry:entry_ptr']),
        ))
        db.send_create_signal('core', ['PageEntry'])
        
        # Adding model 'ImageEntry'
        db.create_table('cms_imageentry', (
            ('entry_ptr', orm['core.ImageEntry:entry_ptr']),
        ))
        db.send_create_signal('core', ['ImageEntry'])
        
        # Adding model 'VInternalRedirection'
        db.create_table('cms_vinternalredirection', (
            ('vobject_ptr', orm['core.VInternalRedirection:vobject_ptr']),
            ('target', orm['core.VInternalRedirection:target']),
        ))
        db.send_create_signal('core', ['VInternalRedirection'])
        
        # Adding model 'Lentity'
        db.create_table('cms_lentity', (
            ('id', orm['core.Lentity:id']),
            ('user', orm['core.Lentity:user']),
            ('group', orm['core.Lentity:group']),
            ('special', orm['core.Lentity:special']),
        ))
        db.send_create_signal('core', ['Lentity'])
        
        # Adding model 'ContentFormat'
        db.create_table('cms_contentformat', (
            ('id', orm['core.ContentFormat:id']),
            ('descr', orm['core.ContentFormat:descr']),
        ))
        db.send_create_signal('core', ['ContentFormat'])
        
        # Adding ManyToManyField 'Workflow.states'
        db.create_table('cms_workflow_states', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workflow', models.ForeignKey(orm.Workflow, null=False)),
            ('state', models.ForeignKey(orm.State, null=False))
        ))
        
        # Adding ManyToManyField 'Workflow.state_transitions'
        db.create_table('cms_workflow_state_transitions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workflow', models.ForeignKey(orm.Workflow, null=False)),
            ('statetransition', models.ForeignKey(orm.StateTransition, null=False))
        ))
        
        # Creating unique_together for [entry, version_number] on VObject.
        db.create_unique('cms_vobject', ['entry_id', 'version_number'])
        
        # Creating unique_together for [container, seq] on Entry.
        db.create_unique('cms_entry', ['container_id', 'seq'])
        
        # Creating unique_together for [lentity, permission] on EntryPermission.
        db.create_unique('cms_entrypermission', ['lentity_id', 'permission_id'])
        
        # Creating unique_together for [vobject, language] on VObjectMetatags.
        db.create_unique('cms_vobjectmetatags', ['vobject_id', 'language_id'])
        
        # Creating unique_together for [lentity, permission] on StatePermission.
        db.create_unique('cms_statepermission', ['lentity_id', 'permission_id'])
        
        # Creating unique_together for [user, group] on Lentity.
        db.create_unique('cms_lentity', ['user_id', 'group_id'])
        
        # Creating unique_together for [source_state, target_state] on StateTransition.
        db.create_unique('cms_statetransition', ['source_state_id', 'target_state_id'])
        
        # Creating unique_together for [container, name] on Entry.
        db.create_unique('cms_entry', ['container_id', 'name'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [container, name] on Entry.
        db.delete_unique('cms_entry', ['container_id', 'name'])
        
        # Deleting unique_together for [source_state, target_state] on StateTransition.
        db.delete_unique('cms_statetransition', ['source_state_id', 'target_state_id'])
        
        # Deleting unique_together for [user, group] on Lentity.
        db.delete_unique('cms_lentity', ['user_id', 'group_id'])
        
        # Deleting unique_together for [lentity, permission] on StatePermission.
        db.delete_unique('cms_statepermission', ['lentity_id', 'permission_id'])
        
        # Deleting unique_together for [vobject, language] on VObjectMetatags.
        db.delete_unique('cms_vobjectmetatags', ['vobject_id', 'language_id'])
        
        # Deleting unique_together for [lentity, permission] on EntryPermission.
        db.delete_unique('cms_entrypermission', ['lentity_id', 'permission_id'])
        
        # Deleting unique_together for [container, seq] on Entry.
        db.delete_unique('cms_entry', ['container_id', 'seq'])
        
        # Deleting unique_together for [entry, version_number] on VObject.
        db.delete_unique('cms_vobject', ['entry_id', 'version_number'])
        
        # Deleting model 'Permission'
        db.delete_table('cms_permission')
        
        # Deleting model 'Entry'
        db.delete_table('cms_entry')
        
        # Deleting model 'VPage'
        db.delete_table('cms_vpage')
        
        # Deleting model 'VImage'
        db.delete_table('cms_vimage')
        
        # Deleting model 'VObject'
        db.delete_table('cms_vobject')
        
        # Deleting model 'VLink'
        db.delete_table('cms_vlink')
        
        # Deleting model 'Language'
        db.delete_table('cms_language')
        
        # Deleting model 'StatePermission'
        db.delete_table('cms_statepermission')
        
        # Deleting model 'StateTransition'
        db.delete_table('cms_statetransition')
        
        # Deleting model 'Workflow'
        db.delete_table('cms_workflow')
        
        # Deleting model 'LinkEntry'
        db.delete_table('cms_linkentry')
        
        # Deleting model 'State'
        db.delete_table('cms_state')
        
        # Deleting model 'EntryPermission'
        db.delete_table('cms_entrypermission')
        
        # Deleting model 'VObjectMetatags'
        db.delete_table('cms_vobjectmetatags')
        
        # Deleting model 'InternalRedirectionEntry'
        db.delete_table('cms_internalredirectionentry')
        
        # Deleting model 'PageEntry'
        db.delete_table('cms_pageentry')
        
        # Deleting model 'ImageEntry'
        db.delete_table('cms_imageentry')
        
        # Deleting model 'VInternalRedirection'
        db.delete_table('cms_vinternalredirection')
        
        # Deleting model 'Lentity'
        db.delete_table('cms_lentity')
        
        # Deleting model 'ContentFormat'
        db.delete_table('cms_contentformat')
        
        # Dropping ManyToManyField 'Workflow.states'
        db.delete_table('cms_workflow_states')
        
        # Dropping ManyToManyField 'Workflow.state_transitions'
        db.delete_table('cms_workflow_state_transitions')
        
    
    
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
