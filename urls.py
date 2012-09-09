from django.conf.urls.defaults import patterns, include, url
from app.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # URLS
    (r'^$', splash),
    url(r'^top/$', 'app.views.splash',{'show':'top'},'splash-top'),
    url(r'^started/$', 'app.views.splash',{'show':'started'},'splash-started'),
    url(r'^not-started/$', 'app.views.splash',{'show':'not-started'},'splash-not-started'),
    url(r'^idea/(?P<idea_id>\w+)/edit/$',
        'app.views.idea',
        {'edit':'true'},
        'edit-idea'
        ),
    url(r'^idea/(?P<idea_id>\w+)/delete/$',
        'app.views.delete_idea',
        name='delete-idea'
        ),
    url(r'^idea/(?P<idea_id>\w+)/$',
        'app.views.idea',
        name = 'idea',
        ),
    (r'^bookmarklet/idea/$', bookmarklet),
    # ADMIN
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # USER MANAGEMENT
    (r'^accounts/verify/(?P<username>\w+)/(?P<verify_hash>\w+)/$', verify),    
    (r'^accounts/register/$', register),
    (r'^accounts/profile/$', profile),
    url(r'^accounts/password/$', 
        'app.views.password',
        name='password'),
    url(r'^accounts/pw_rst/(?P<user_id>\w+)/(?P<hashed>\w+)/$',
        'app.views.password_reset',
        name='password_reset'),
    
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':
        'main/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page':'/accounts/login/'}),

    (r'^accounts/facebook/$', facebook),

    # API
    (r'^api/', include('app.api.urls')),

)

