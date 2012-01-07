from piston.handler import BaseHandler
from glossy_app.models import Language 

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

