# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Slate'
        db.create_table('app_slate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('app', ['Slate'])

        # Adding M2M table for field users on 'Slate'
        db.create_table('app_slate_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('slate', models.ForeignKey(orm['app.slate'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('app_slate_users', ['slate_id', 'user_id'])

        # Adding M2M table for field ideas on 'Slate'
        db.create_table('app_slate_ideas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('slate', models.ForeignKey(orm['app.slate'], null=False)),
            ('idea', models.ForeignKey(orm['app.idea'], null=False))
        ))
        db.create_unique('app_slate_ideas', ['slate_id', 'idea_id'])


    def backwards(self, orm):
        
        # Deleting model 'Slate'
        db.delete_table('app_slate')

        # Removing M2M table for field users on 'Slate'
        db.delete_table('app_slate_users')

        # Removing M2M table for field ideas on 'Slate'
        db.delete_table('app_slate_ideas')


    models = {
        'app.comment': {
            'Meta': {'object_name': 'Comment'},
            'date_posted': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'idea_comment'", 'to': "orm['app.Idea']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_comment'", 'to': "orm['auth.User']"})
        },
        'app.idea': {
            'Meta': {'object_name': 'Idea'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'elaborate': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.TextField', [], {}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_idea'", 'to': "orm['auth.User']"})
        },
        'app.slate': {
            'Meta': {'object_name': 'Slate'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ideas': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Idea']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'app.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_idea'", 'to': "orm['app.Idea']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'default_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'facebook_access_token': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'temp_hash': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'extra'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'app.vote': {
            'Meta': {'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_on'", 'to': "orm['app.Idea']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_vote'", 'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
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
        }
    }

    complete_apps = ['app']
