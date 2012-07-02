from django.conf.urls.defaults import *
from piston.resource import Resource
from glossy_app.api.handlers import LanguageHandler

language_handler = Resource(LanguageHandler)

urlpatterns = patterns('',
   url(r'^idea/(?P<language_id>[^/]+)/', language_handler),
   url(r'^ideas/', language_handler),
)

