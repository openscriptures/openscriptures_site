from django.conf.urls.defaults import *

from interest_groups.models import InterestGroup

from groups.bridge import ContentBridge


bridge = ContentBridge(InterestGroup, 'interest_groups')

urlpatterns = patterns('interest_groups.views',
    url(r'^$', 'interest_groups', name="interest_group_list"),
    url(r'^create/$', 'create', name="interest_group_create"),
    url(r'^your_interest_groups/$', 'your_interest_groups', name="your_interest_groups"),
    
    # interest-group-specific
    url(r'^interest_group/(?P<group_slug>[-\w]+)/$', 'interest_group', name="interest_group_detail"),
    url(r'^interest_group/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="interest_group_delete"),
)

urlpatterns += bridge.include_urls('topics.urls', r'^interest_group/(?P<group_slug>[-\w]+)/topics/')
urlpatterns += bridge.include_urls('wiki.urls', r'^interest_group/(?P<group_slug>[-\w]+)/wiki/')
