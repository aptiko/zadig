# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Language'
        db.create_table('zadig_language', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=5, primary_key=True)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('core', ['Language'])

        # Adding model 'Permission'
        db.create_table('zadig_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=31)),
        ))
        db.send_create_signal('core', ['Permission'])

        # Adding model 'Lentity'
        db.create_table('zadig_lentity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True)),
            ('special', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
        ))
        db.send_create_signal('core', ['Lentity'])

        # Adding unique constraint on 'Lentity', fields ['user', 'group']
        db.create_unique('zadig_lentity', ['user_id', 'group_id'])

        # Adding model 'State'
        db.create_table('zadig_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=31)),
        ))
        db.send_create_signal('core', ['State'])

        # Adding model 'StatePermission'
        db.create_table('zadig_statepermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.State'])),
            ('lentity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Lentity'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Permission'])),
        ))
        db.send_create_signal('core', ['StatePermission'])

        # Adding model 'StateTransition'
        db.create_table('zadig_statetransition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_rules', to=orm['core.State'])),
            ('target_state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='target_rules', to=orm['core.State'])),
        ))
        db.send_create_signal('core', ['StateTransition'])

        # Adding unique constraint on 'StateTransition', fields ['source_state', 'target_state']
        db.create_unique('zadig_statetransition', ['source_state_id', 'target_state_id'])

        # Adding model 'Workflow'
        db.create_table('zadig_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=127)),
        ))
        db.send_create_signal('core', ['Workflow'])

        # Adding M2M table for field states on 'Workflow'
        db.create_table('zadig_workflow_states', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workflow', models.ForeignKey(orm['core.workflow'], null=False)),
            ('state', models.ForeignKey(orm['core.state'], null=False))
        ))
        db.create_unique('zadig_workflow_states', ['workflow_id', 'state_id'])

        # Adding M2M table for field state_transitions on 'Workflow'
        db.create_table('zadig_workflow_state_transitions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workflow', models.ForeignKey(orm['core.workflow'], null=False)),
            ('statetransition', models.ForeignKey(orm['core.statetransition'], null=False))
        ))
        db.create_unique('zadig_workflow_state_transitions', ['workflow_id', 'statetransition_id'])

        # Adding model 'MultilingualGroup'
        db.create_table('zadig_multilingualgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['MultilingualGroup'])

        # Adding model 'Entry'
        db.create_table('zadig_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_class', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='all_subentries', null=True, to=orm['core.Entry'])),
            ('name', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=100, blank=True)),
            ('seq', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.State'])),
            ('multilingual_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MultilingualGroup'], null=True, blank=True)),
            ('btemplate', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('core', ['Entry'])

        # Adding unique constraint on 'Entry', fields ['container', 'name']
        db.create_unique('zadig_entry', ['container_id', 'name'])

        # Adding unique constraint on 'Entry', fields ['container', 'seq']
        db.create_unique('zadig_entry', ['container_id', 'seq'])

        # Adding model 'EntryPermission'
        db.create_table('zadig_entrypermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Entry'])),
            ('lentity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Lentity'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Permission'])),
        ))
        db.send_create_signal('core', ['EntryPermission'])

        # Adding unique constraint on 'EntryPermission', fields ['lentity', 'permission']
        db.create_unique('zadig_entrypermission', ['lentity_id', 'permission_id'])

        # Adding model 'VObject'
        db.create_table('zadig_vobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_class', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vobject_set', to=orm['core.Entry'])),
            ('version_number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Language'], null=True, blank=True)),
            ('deletion_mark', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['VObject'])

        # Adding unique constraint on 'VObject', fields ['entry', 'version_number']
        db.create_unique('zadig_vobject', ['entry_id', 'version_number'])

        # Adding model 'VObjectMetatags'
        db.create_table('zadig_vobjectmetatags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vobject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metatags_set', to=orm['core.VObject'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Language'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('short_title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['VObjectMetatags'])

        # Adding unique constraint on 'VObjectMetatags', fields ['vobject', 'language']
        db.create_unique('zadig_vobjectmetatags', ['vobject_id', 'language_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'VObjectMetatags', fields ['vobject', 'language']
        db.delete_unique('zadig_vobjectmetatags', ['vobject_id', 'language_id'])

        # Removing unique constraint on 'VObject', fields ['entry', 'version_number']
        db.delete_unique('zadig_vobject', ['entry_id', 'version_number'])

        # Removing unique constraint on 'EntryPermission', fields ['lentity', 'permission']
        db.delete_unique('zadig_entrypermission', ['lentity_id', 'permission_id'])

        # Removing unique constraint on 'Entry', fields ['container', 'seq']
        db.delete_unique('zadig_entry', ['container_id', 'seq'])

        # Removing unique constraint on 'Entry', fields ['container', 'name']
        db.delete_unique('zadig_entry', ['container_id', 'name'])

        # Removing unique constraint on 'StateTransition', fields ['source_state', 'target_state']
        db.delete_unique('zadig_statetransition', ['source_state_id', 'target_state_id'])

        # Removing unique constraint on 'Lentity', fields ['user', 'group']
        db.delete_unique('zadig_lentity', ['user_id', 'group_id'])

        # Deleting model 'Language'
        db.delete_table('zadig_language')

        # Deleting model 'Permission'
        db.delete_table('zadig_permission')

        # Deleting model 'Lentity'
        db.delete_table('zadig_lentity')

        # Deleting model 'State'
        db.delete_table('zadig_state')

        # Deleting model 'StatePermission'
        db.delete_table('zadig_statepermission')

        # Deleting model 'StateTransition'
        db.delete_table('zadig_statetransition')

        # Deleting model 'Workflow'
        db.delete_table('zadig_workflow')

        # Removing M2M table for field states on 'Workflow'
        db.delete_table('zadig_workflow_states')

        # Removing M2M table for field state_transitions on 'Workflow'
        db.delete_table('zadig_workflow_state_transitions')

        # Deleting model 'MultilingualGroup'
        db.delete_table('zadig_multilingualgroup')

        # Deleting model 'Entry'
        db.delete_table('zadig_entry')

        # Deleting model 'EntryPermission'
        db.delete_table('zadig_entrypermission')

        # Deleting model 'VObject'
        db.delete_table('zadig_vobject')

        # Deleting model 'VObjectMetatags'
        db.delete_table('zadig_vobjectmetatags')


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
        'core.entrypermission': {
            'Meta': {'unique_together': "(('lentity', 'permission'),)", 'object_name': 'EntryPermission', 'db_table': "'zadig_entrypermission'"},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lentity']"}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']"})
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
        'core.multilingualgroup': {
            'Meta': {'object_name': 'MultilingualGroup', 'db_table': "'zadig_multilingualgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'Meta': {'object_name': 'StatePermission', 'db_table': "'zadig_statepermission'"},
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
        'core.vobjectmetatags': {
            'Meta': {'unique_together': "(('vobject', 'language'),)", 'object_name': 'VObjectMetatags', 'db_table': "'zadig_vobjectmetatags'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Language']"}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'vobject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metatags_set'", 'to': "orm['core.VObject']"})
        },
        'core.workflow': {
            'Meta': {'object_name': 'Workflow', 'db_table': "'zadig_workflow'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'state_transitions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.StateTransition']", 'symmetrical': 'False'}),
            'states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.State']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['core']
