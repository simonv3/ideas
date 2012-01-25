from piston.handler import BaseHandler
from django.controbi.auth.models import  User


class UserHandler(BaseHandler):
    allowed_methods= ('GET',)
    model = User
    def read(self, request, user_id=None)
        base = User

class LanguageHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Language   
    def read(self, request, language_id=None):
   
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        base = Language.objects
        
        if language_id:
            return base.get(pk=language_id)
        else:
            return base.all()

