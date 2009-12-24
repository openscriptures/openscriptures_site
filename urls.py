import os

from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer


if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "signup_codes.views.signup"


# override the default handler500 so we can pass MEDIA_URL
handler500 = "openscriptures_site.views.server_error"


urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    
    url(r'^admin/invite_user/$', 'signup_codes.views.admin_invite_user', name="admin_invite_user"),
    url(r'^account/signup/$', signup_view, name="acct_signup"),
    
    url(r'^blog/', include("biblion.urls")),
    url(r'^feed/$', "biblion.views.blog_feed", name="blog_feed_combined"),
    url(r'^feed/(?P<section>[-\w]+)/$', "biblion.views.blog_feed", name="blog_feed"),
    
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),
    
    (r'^profiles/', include('basic_profiles.urls')),
    
    url(r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('', 
        (r'^site_media/', include('staticfiles.urls')),
    )
