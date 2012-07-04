from django.conf.urls.defaults import *
from piston.resource import Resource
from app.api.handlers import IdeaHandler, UserHandler, UserIdeasHandler

idea_handler = Resource(IdeaHandler)
user_handler = Resource(UserHandler)
user_ideas_handler = Resource(UserIdeasHandler)

urlpatterns = patterns('',
    url(r'^idea/(?P<idea_id>[^/]+)/', idea_handler),
    url(r'^ideas/', idea_handler),

    url(r'^user/(?P<user_id>[^/]+)/ideas/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_ideas_handler),
    url(r'^user/(?P<user_id>[^/]+)/', user_handler),

    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),

)

