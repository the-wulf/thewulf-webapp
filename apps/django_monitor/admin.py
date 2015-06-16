
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.contrib.admin.filterspecs import FilterSpec
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper
from django.template import RequestContext
from django.utils.safestring import mark_safe

from django_monitor.actions import (
    approve_selected, challenge_selected, reset_to_pending
)
from django_monitor.filter import MonitorFilter
from django_monitor import model_from_queue, queued_models
from django_monitor.conf import (
    PENDING_STATUS, CHALLENGED_STATUS, APPROVED_STATUS,
    PENDING_DESCR, CHALLENGED_DESCR
)
from django_monitor.models import MonitorEntry

# Our objective is to place the custom monitor-filter on top
FilterSpec.filter_specs.insert(
    0, (lambda f: getattr(f, 'monitor_filter', False), MonitorFilter)
)

class HiddenModelsAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict if not superuser thus hiding the model from admin index.
        """
        if request.user.is_superuser:
            return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            }
        else:
            return {}


class MEAdmin(HiddenModelsAdmin):
    """
    A special admin-class for aggregating moderation summary, not to let users
    add/edit/delete MonitorEntry objects directly. MonitorEntry works from
    behind the curtain. This admin class is to provide a single stop for users
    to get notified about pending/challenged model objects.
    """
    change_list_template = 'admin/django_monitor/monitorentry/change_list.html'

    def get_urls(self):
        """ The only url allowed is that for changelist_view. """
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name = '%s_%s_changelist' % info
            ),
        )
        return urlpatterns

    def has_add_permission(self, request, obj = None):
        """ Returns False so that no add button is displayed in admin index"""
        return False

    def has_change_permission(self, request, obj = None):
        """
        Users will be lead to the moderation summary page when they click on
        the link for changelist, which has a url like,
        ``/admin/django_monitor/monitorentry/``. The admin site index page will show
        the link to user, only if they have change_permission. So lets grant
        that perm to all admin-users.
        """
        if obj is None and request.user.is_active and request.user.is_staff:
            return True
        return super(MEAdmin, self).has_change_permission(request, obj)

    def changelist_view(self, request, extra_context = None):
        """
        The 'change list' admin view is overridden to return a page showing the
        moderation summary aggregated for each model.
        """
        model_list = []
        for model in queued_models():
            # I do not like to access private objects. No other option here!
            # Get only those objects developer wish to let user see..
            try:
                model_admin = self.admin_site._registry[model]
            except KeyError:
                # This may happen at test-time. There the ``queued_models``
                # come from the project where the test is actually being run
                # but the admin_site registry knows only those models in
                # ``django_monitor.tests.apps.testapp.models``.
                continue

            ip_count = model_admin.queryset(request).pending().count()
            ch_count = model_admin.queryset(request).challenged().count()

            app_label = model._meta.app_label
            if ip_count or ch_count:
                model_list.append({
                    'model_name': model._meta.verbose_name,
                    'app_name': app_label.title(),
                    'pending': ip_count, 'challenged': ch_count,
                    'admin_url': mark_safe(
                        '/admin/%s/%s/' % (app_label, model.__name__.lower())
                    ),
                })
        model_list.sort(key = lambda x: (x['app_name'], x['model_name']))
        return render_to_response(
            self.change_list_template,
            {
                'model_list': model_list,
                'ip_status': PENDING_STATUS, 'ip_descr': PENDING_DESCR,
                'ch_status': CHALLENGED_STATUS, 'ch_descr': CHALLENGED_DESCR
            },
            context_instance = RequestContext(request)
        )

admin.site.register(MonitorEntry, MEAdmin)

class MonitorAdmin(admin.ModelAdmin):
    """ModelAdmin for monitored models should inherit this."""

    # Which fields are to be made readonly after approval.
    protected_fields = ()

    def __init__(self, model, admin_site):
        """ Overridden to add a custom filter to list_filter """
        super(MonitorAdmin, self).__init__(model, admin_site)
        self.list_filter = ['id'] + list(self.list_filter)
        self.list_display = (
            list(self.list_display) + ['get_monitor_status_display']
        )

    def queryset(self, request):
        """
        Django does not allow using non-fields in list_filter. (As of 1.3).
        Using params not mentioned in list_filter will raise error in changelist.
        We want to enable status based filtering (status is not a db_field).
        We will check the request.GET here and if there's a `status` in it,
        Remove that and filter the qs by status.
        """
        qs = super(MonitorAdmin, self).queryset(request)
        status = request.GET.get('status', None)
        # status is not among list_filter entries. So its presence will raise
        # IncorrectLookupParameters when django tries to build-up changelist.
        # So let's remove it from GET dict (Still available in the url.)
        if status:
            get_dict = request.GET.copy()
            del get_dict['status']
            request.GET = get_dict
        # ChangeList will use this custom queryset. So we've done it!
        if status and status == PENDING_STATUS:
            qs = qs.pending()
        elif status and status == CHALLENGED_STATUS:
            qs = qs.challenged()
        elif status and status == APPROVED_STATUS:
            qs = qs.approved()
        return qs

    def is_monitored(self):
        """Returns whether the underlying model is monitored or not."""
        return bool(model_from_queue(self.model))

# need to fix this on add abstract ...
#    def get_readonly_fields(self, request, obj = None):
#        """ Overridden to include protected_fields as well."""
#        if (
#            self.is_monitored() and 
#            obj is not None and obj.is_approved
#        ):
#            return self.readonly_fields + self.protected_fields
#        return self.readonly_fields

    def get_actions(self, request):
        """ For monitored models, we need 3 more actions."""
        actions = super(MonitorAdmin, self).get_actions(request)
        mod_perm = '%s.moderate_%s' % (
            self.opts.app_label.lower(), self.opts.object_name.lower()
        )
        change_perm = mod_perm.replace('moderate', 'change')
        if request.user.has_perm(mod_perm):
            descr = getattr(
                approve_selected, 'short_description', 'approve selected'
            )
            actions.update({
                'approve_selected': (approve_selected, 'approve_selected', descr)
            })
            descr = getattr(
                challenge_selected, 'short_description', 'challenge selected'
            )
            actions.update({
                'challenge_selected': (challenge_selected, 'challenge_selected', descr)
            })
        if request.user.has_perm(change_perm):
            descr = getattr(
                reset_to_pending, 'short_description', 'reset to pending'
            )
            actions.update({
                'reset_to_pending': (reset_to_pending, 'reset_to_pending', descr)
            })
        return actions

    def has_moderate_permission(self, request):
        """
        Returns true if the given request has permission to moderate objects
        of the model corresponding to this model admin.
        """
        mod_perm = '%s.moderate_%s' % (
            self.opts.app_label.lower(), self.opts.object_name.lower()
        )
        return request.user.has_perm(mod_perm)

    def has_delete_permission(self, request, obj = None):
        """
        If ``can_delete_approved`` is set to False in moderation queue and
        the given object is approved, this will return False. Otherwise,
        this behaves the same way as the parent class method does.
        """
        model = model_from_queue(self.model)
        if (
            model and (not model['can_delete_approved']) and
            obj is not None and obj.is_approved
        ):
            return False
        return super(MonitorAdmin, self).has_delete_permission(request, obj)

