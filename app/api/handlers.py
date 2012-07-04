from piston.handler import BaseHandler
from django.contrib.auth.models import  User
from app.models import Idea

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
    fields = ( ('user', ('id', 'username', 'email', 'date_joined', 'last_login')), 'idea', 'id', )
    def read(self, request,  apikey, apisignature, user_id=None):
        base = Idea.objects
        query="/user/"+user_id+"/ideas/"
        print user_id
        if not key_check(apikey, apisignature,query):
            return {'error':'authentication required'}
        elif user_id:
            return base.filter(user = user_id)
        else:
            return  {'error':'supply user information'}


class IdeaHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id','idea','user','date')

    model = Idea
    def read(self, request, idea_id=None):
   
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        base = Idea.objects
        
        if idea_id:
            return base.get(pk=idea_id)
        else:
            return base.all()

class AuthenticateUser(BaseHandler):
    allow_methods = ('POST',)
    model = User
