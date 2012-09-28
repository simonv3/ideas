from django.conf.urls.defaults import patterns, include, url
from app.views import *
from app.slate import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # URLS
    (r'^$', splash),

    #semi-static
    url(r'^about/$', 'app.views.about', name='about'),


    #functionality
    url(r'^top/$', 'app.views.splash',{'show':'top'},'splash-top'),
    url(r'^started/$', 'app.views.splash',{'show':'started'},'splash-started'),
    url(r'^not-started/$', 'app.views.splash',{'show':'not-started'},'splash-not-started'),

    # IDEA
    url(r'^idea/(?P<idea_id>\w+)/edit/$',
        'app.views.idea',
        {'edit':'true'},
        'edit-idea'
        ),
    url(r'^idea/(?P<idea_id>\w+)/delete/$',
        'app.views.delete_idea',
        name='delete-idea'
        ),
    url(r'^idea/(?P<idea_id>\w+)/start/$',
        'app.views.start_idea',
        name='start-idea'
        ),

    url(r'^idea/(?P<idea_id>\w+)/convert_to_slate/$',
        'app.slate.convert_idea',
        name = 'convert-idea',
        ),

    url(r'^idea/(?P<idea_id>\w+)/$',
        'app.views.idea',
        name = 'idea',
        ),
    (r'^bookmarklet/idea/$', bookmarklet),
    url(r'^search/$',
        'app.views.search',
        name = 'no-query-search',
        ),
    url(r'^search/(?P<query>[\w|\W]+)/$',
        'app.views.search',
        name = 'view-search',
        ),

    # SLATE
    url(r'^slate/(?P<slate_id>\w+)/clean/$',
        'app.slate.clean_slate',
        name='clean-slate'
        ),
    url(r'^slate/(?P<slate_id>\w+)/release/$',
        'app.slate.release_slate',
        name='release-slate'
        ),



    url(r'^slate/(?P<slate_id>\w+)/$',
        'app.slate.view_slate',
        name='view-slate'
        ),
    url(r'^slate/$',
        'app.slate.slate',
        name='slate'
        ),

    # ADMIN
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # USER MANAGEMENT
    (r'^accounts/verify/(?P<id>\w+)/(?P<verify_hash>\w+)/$', verify),    
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

