from django.conf.urls.defaults import patterns, include, url
from thewulf import views
from django.contrib import admin
from django import template

# Uncomment the next line to enable the admin:
admin.autodiscover()

#from moderation.helpers import auto_discover
#auto_discover()

#CUSTOM TEMPLATE TAGS
template.add_to_builtins('thewulf.thewulfcms.templatetags.cmsmodules')

# How do I match all of these in one
urlpatterns = patterns('',
	(r'^grappelli/', include('grappelli.urls')),
	('(^$|^home/$)', 'views.home'),
	('(^events/$)', 'views.events'),
	('(^events/(\d+)/$)', 'views.events_by_year'),
	('(^events/detail/(\d+)/$)', 'views.event_detail'),
	('(^donate/$)', 'views.donate'),
	('(^membership/$)', 'views.membership'),
	('(^media/$)', 'views.media'),
	('(^links/$)', 'views.links'),
	('(^contact/$)', 'views.contact'),
	('(^profiles/$)', 'views.profiles'),
	('(^profiles/(\d+)/$)', 'views.profile'),
#	url(r'^work/', 'views.work', name='rtr'),
    # Examples:
#     url(r'^$', 'thewulf.views.home', name='home'),
    # url(r'^thewulf/', include('thewulf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
