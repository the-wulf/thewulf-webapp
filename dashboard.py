"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = modelPrefix + 'dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name

#import django_monitor

import os


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        modelPrefix = ''
        if os.getcwd()[1:5] == 'home':
            modelPrefix = 'thewulf.'
        
        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Admin Stuff'),
            column=1,
            collapsible=True,
            children = [
                modules.AppList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*','django_monitor.*',),
                ),
#                modules.AppList(
#                    _('Monitor'),
#                    column=1,
#                    collapsible=False,
#                    models=('django_monitor.models.*',),
#                )
            ]
        ))
    
#        self.children.append(modules.Group(
#                _('Moderation Stuff'),
#                column=1,
#                collapsible=True,
#                children = [
#                    modules.AppList(
#                        _('Monitor'),
#                        column=1,
#                        collapsible=False,
#                        models=('moderation.*',),
#                    )
#                ]
#            ))
        
        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('User Stuff'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    _('Profile Stuff'),
                    column=1,
                    css_classes=('collapse open',),
                    models=
                        (modelPrefix + 'thewulfcms.models.AbstractProfile',
                         modelPrefix + 'thewulfcms.models.SingleProfile',
                         modelPrefix + 'thewulfcms.models.GroupProfile',
                         modelPrefix + 'thewulfcms.models.VenueProfile',
                         modelPrefix + 'thewulfcms.models.ProfileAudioRecording',
                         modelPrefix + 'thewulfcms.models.ProfilePic',
                         modelPrefix + 'thewulfcms.models.ProfileVideo',
                         modelPrefix + 'thewulfcms.models.Instrument',
                         )
                    ),
                modules.ModelList(
                    _('Event Stuff'),
                    column=1,
                    css_classes=('collapse open',),
                    models=
                        (
                        modelPrefix + 'thewulfcms.models.AbstractEvent',
                         modelPrefix + 'thewulfcms.models.Event',
                         modelPrefix + 'thewulfcms.models.Installation',
                         modelPrefix + 'thewulfcms.models.Performer',
                         modelPrefix + 'thewulfcms.models.Program',
                         modelPrefix + 'thewulfcms.models.EventAudioRecording',
                         modelPrefix + 'thewulfcms.models.EventPic',
                         modelPrefix + 'thewulfcms.models.EventVideo',
                         ),
                    ),
                modules.ModelList(
                    _('Work Stuff'),
                    column=1,
                    css_classes=('collapse open',),
                    models=
                        (modelPrefix + 'thewulfcms.models.AbstractWork',
                         modelPrefix + 'thewulfcms.models.Work',
                         modelPrefix + 'thewulfcms.models.Movement',
                         ),
                    ),
                modules.ModelList(
                    _('Post Stuff'),
                    column=1,
                    css_classes=('collapse open',),
                    models=
                        (modelPrefix + 'thewulfcms.models.Post',
                         modelPrefix + 'thewulfcms.models.Category',
                         modelPrefix + 'thewulfcms.models.PostAudioRecording',
                         modelPrefix + 'thewulfcms.models.PostPic',
                         modelPrefix + 'thewulfcms.models.PostVideo',
                         ),
                    ),
            ]
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=2,
            children=[
                {
                    'title': _('FileBrowser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))
        
#        # append another link list module for "support".
#        self.children.append(modules.LinkList(
#            _('Support'),
#            column=2,
#            children=[
#                {
#                    'title': _('Django Documentation'),
#                    'url': 'http://docs.djangoproject.com/',
#                    'external': True,
#                },
#                {
#                    'title': _('Grappelli Documentation'),
#                    'url': 'http://packages.python.org/django-grappelli/',
#                    'external': True,
#                },
#                {
#                    'title': _('Grappelli Google-Code'),
#                    'url': 'http://code.google.com/p/django-grappelli/',
#                    'external': True,
#                },
#            ]
#        ))
#        
#        # append a feed module
#        self.children.append(modules.Feed(
#            _('Latest Django News'),
#            column=2,
#            feed_url='http://www.djangoproject.com/rss/weblog/',
#            limit=5
#        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))


