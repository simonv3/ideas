from django.conf.urls.defaults import *
from piston.resource import Resource
from glossy_app.api.handlers import LanguageHandler

language_handler = Resource(LanguageHandler)

urlpatterns = patterns('',
   url(r'^language/(?P<language_id>[^/]+)/', language_handler),
   url(r'^languages/', language_handler),
)

