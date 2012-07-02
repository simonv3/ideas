from django.conf.urls.defaults import *
from piston.resource import Resource
from app.api.handlers import IdeaHandler

idea_handler = Resource(IdeaHandler)

urlpatterns = patterns('',
   url(r'^idea/(?P<idea_id>[^/]+)/', idea_handler),
   url(r'^ideas/', idea_handler),
)

