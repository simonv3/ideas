from piston.handler import BaseHandler
from django.contrib.auth.models import  User
from app.models import Idea
from app.forms import IdeaForm

from app.api.auth import key_check, secrets


class UserHandler(BaseHandler):
    allowed_methods= ('GET',)
    model = User
    fields = ('username','is_active','last_login','email','date_joined')
    def read(self, request, user_id=None):
        base = User.objects
        if user_id:
            return base.get(pk=user_id)
        else:
            return {'error':'supply user information'}


class UserIdeasHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Idea
    fields = ((
        'user', 
        ('id', 'username', 'email', 'date_joined', 'last_login')), 
        'idea', 'id', )
    def read(self, request,  apikey, apisignature, user_id=None):
        base = Idea.objects
        query="/user/"+user_id+"/ideas/"
        #print user_id
        if not key_check(apikey, apisignature,query):
            return {'error':'authentication required'}
        elif user_id:
            return base.filter(user = user_id)
        else:
            return  {'error':'supply user information'}


class PostIdeaHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id', 'idea', 'user', 'date')
    model = Idea
    def read(
            self, request, idea_text, user_id, 
            apikey, apisignature, idea_tags=None):
        if not key_check( apikey, apisignature, '/idea/%s/%s/' % (user_id, idea_text)):
            return {'error':'authentication failed'}
        else:
            ideaForm = IdeaForm({"idea_content":idea_text})
            if ideaForm.is_valid():
                clean = ideaForm.cleaned_data
                idea = Idea(idea=clean['idea_content'], user = User.objects.get(id = user_id))
                idea.save()
                return idea



class IdeaHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id','idea','user','date')
    model = Idea
    def read(self, request, idea_id=None):
        base = Idea.objects
        if idea_id:
            return base.get(pk=idea_id)
        else:
            return base.all()

class UserRegistrationHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(
            self, request, username, 
            password, apikey, apisignature, 
            ):
        if not key_check(
                apikey, apisignature, 
                '/register/%s/%s/' % (username, password)):
            return {'error': 'authentication failed'}
        print "get here2"
        try: 
            User.objects.get(username=username)
            return {'registration' : 'failure', 'reason' : 'exists' }
        except:
            user = User.objects.create_user(username,'',password)
            user.save()
            return user
        #return tigatag.views.login.register_basic(request, username, password, email)

class UserLogInHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(
            self, request, username, 
            password, apikey, apisignature):
        if not key_check(
                apikey, apisignature, 
                '/login/%s/%s/' % (username, password)):
            return {'error': 'authentication failed'}
        else:
            from django.contrib.auth import authenticate
            user_in_db = authenticate(username=username,password=password)
            if user_in_db:
                return user_in_db
            else:
                return {'error':'not a user'}


class AuthenticateUser(BaseHandler):
    allow_methods = ('POST',)
    model = User
