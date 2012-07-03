from piston.handler import BaseHandler
from django.contrib.auth.models import  User
from app.models import Idea

class UserHandler(BaseHandler):
    allowed_methods= ('GET',)
    model = User
    def read(self, request, user_id=None):
        base = User

class IdeaHandler(BaseHandler):
    allowed_methods = ('GET',)
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
