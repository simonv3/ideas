from django.conf.urls.defaults import *
from piston.resource import Resource
from app.api.handlers import IdeaHandler, UserHandler, UserIdeasHandler,UserLogInHandler, UserRegistrationHandler, PostIdeaHandler

idea_handler = Resource(IdeaHandler)
post_idea_handler = Resource(PostIdeaHandler)
user_handler = Resource(UserHandler)
user_ideas_handler = Resource(UserIdeasHandler)
user_registration_handler = Resource(UserRegistrationHandler)
user_log_in_handler = Resource(UserLogInHandler)

urlpatterns = patterns('',
    #url(r'^idea/(?P<user_id>[^/]+)/(?P<idea_text>[^/]+)/(?P<idea_tags>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', post_idea_handler),
    url(r'^idea/(?P<user_id>[^/]+)/(?P<idea_text>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', post_idea_handler),
    url(r'^idea/(?P<idea_id>[^/]+)/', idea_handler),
    url(r'^ideas/', idea_handler),

    url(r'^user/(?P<user_id>[^/]+)/ideas/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_ideas_handler),
    url(r'^user/(?P<user_id>[^/]+)/', user_handler),

    url(r'^register/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_registration_handler),
    url(r'^login/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_log_in_handler),
    #'piston.authentication',
    #url(r'^oauth/request_token/$','oauth_request_token'),
    #url(r'^oauth/authorize/$','oauth_user_auth'),
    #url(r'^oauth/access_token/$','oauth_access_token'),

)

