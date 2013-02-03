from django.conf.urls.defaults import *
from django.http import HttpResponse
from piston.resource import Resource
from app.api.handlers import IdeasHandler, UserLogInHandler, UserRegistrationHandler, SlatesHandler, CommentHandler, VoteHandler

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt, and to enable CORS"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)
    # adding cors enablement

    cors_headers = [
        ('Access-Control-Allow-Origin',     '*'),
        ('Access-Control-Allow-Headers',    'X-Requested-With, Authorization'),
    ]

    # headers sent in pre-flight responses
    preflight_headers = cors_headers + [
        ('Access-Control-Allow-Methods',    'GET, POST, OPTIONS, DELETE'),
        ('Access-Control-Allow-Credentials','true')
    ]

    def __call__(self, request, *args, **kwargs):
        request_method = request.method.upper()
        # intercept OPTIONS method requests
        if request_method == "OPTIONS":
            # preflight requests don't need a body, just headers
            resp = HttpResponse()
            # add headers to the empty response
            for hk, hv in self.preflight_headers:
                resp[hk] = hv


        else:
            # otherwise, behave as if we called  the base Resource
            resp = super(CsrfExemptResource, self).__call__(request, *args, **kwargs)

            # slip in the headers after we get the response
            # from the handler
            for hk, hv in self.cors_headers:
                resp[hk] = hv
        return resp

comment_handler = CsrfExemptResource(CommentHandler)
ideas_handler = CsrfExemptResource(IdeasHandler)
user_slates_handler = CsrfExemptResource(SlatesHandler)
user_registration_handler = CsrfExemptResource(UserRegistrationHandler)
user_log_in_handler = CsrfExemptResource(UserLogInHandler)
votes_handler = CsrfExemptResource(VoteHandler)

urlpatterns = patterns('',
    url(r'^idea/post/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', ideas_handler),
    
    # handle comments
    url(r'^idea/(?P<idea_id>[^/]+)/comments/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', comment_handler),

    url(r'^idea/comment/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', comment_handler),

    url(r'^idea/like/(?P<idea_id>\d+)/(?P<user_id>\d+)/(?P<vote_value>\d{1})/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', votes_handler),

    url(r'^idea/delete/(?P<idea_id>[^/]+)/(?P<user_id>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', ideas_handler),


    url(r'^ideas/$', ideas_handler),

    url(r'^user/(?P<user_id>[^/]+)/(?P<fetch_all>[^/]+)/ideas/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', ideas_handler),

    url(r'^user/(?P<user_id>[^/]+)/slates/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_slates_handler),

    #url(r'^user/(?P<user_id>[^/]+)/', user_handler),

    url(r'^register/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_registration_handler),
    url(r'^login/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_log_in_handler),

    #url(r'^register/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_registration_handler),
    #url(r'^login/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<apikey>[^/]+)/(?P<apisignature>[^/]+)/', user_log_in_handler),
    #'piston.authentication',
    #url(r'^oauth/request_token/$','oauth_request_token'),
    #url(r'^oauth/authorize/$','oauth_user_auth'),
    #url(r'^oauth/access_token/$','oauth_access_token'),

)

