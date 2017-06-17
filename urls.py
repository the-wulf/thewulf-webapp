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
urlpatterns = patterns(
    '',
    (r'^grappelli/', include('grappelli.urls')),
    ('(^$)', 'views.home'),
    ('(^about/$)', 'views.about'),
    ('(^events/$)', 'views.events'),
    ('(^events/(\d+)/$)', 'views.events_by_year'),
    url('(^events/details/(\d+)/$)', 'views.event_details', name='event_details'),
    ('(^donate/$)', 'views.donate'),
    ('(^membership/$)', 'views.membership'),
    ('(^media/$)', 'views.media'),
    ('(^links/$)', 'views.links'),
    ('(^contact/$)', 'views.contact'),
    ('(^profiles/$)', 'views.profiles'),
    ('(^profiles/(\d+)/$)', 'views.profile'),

    url(r'^archive/$', 'views.archive_list', name='archive_list'),
    url(r'^archive/(?P<year>20\d{2})/$', 'views.archive_list', name='archive_list_by_year'),
    url(r'^archive/(?P<year>20\d{2})/(?P<month>\d{2})/$', 'views.archive_list', name='archive_list_by_month'),
    url(r'^archive/program/(?P<program_id>\d+)/$', 'views.archive_list', name='archive_detail'),

#	url(r'^work/', 'views.work', name='rtr'),
    # Examples:
#     url(r'^$', 'thewulf.views.home', name='home'),
    # url(r'^thewulf/', include('thewulf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
