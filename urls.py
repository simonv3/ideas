from django.conf.urls.defaults import patterns, include, url
from app.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # URLS
    (r'^$', splash),
    (r'^idea/(?P<idea_id>\w+)/edit/$', idea, {'edit':'true'}),
    (r'^idea/(?P<idea_id>\w+)/$', idea),
    (r'^bookmarklet/idea/$', bookmarklet),
     
    # ADMIN
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # USER MANAGEMENT
    (r'^accounts/verify/(?P<username>\w+)/(?P<verify_hash>\w+)/$', verify),    
    (r'^accounts/register/$', register),
    (r'^accounts/profile/$', profile),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':
        'main/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page':'/accounts/login/'}),

)

