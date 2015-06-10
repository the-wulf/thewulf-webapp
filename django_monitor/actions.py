
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import model_ngettext
from django.utils.translation import ugettext_lazy, ugettext as _

from django_monitor.util import moderate_rel_objects
from django_monitor import model_from_queue
from django_monitor.conf import (
    STATUS_DICT, PENDING_STATUS, APPROVED_STATUS, CHALLENGED_STATUS
)
from django_monitor.models import MonitorEntry

def moderate_selected(modeladmin, request, queryset, status):
    """
    Generic action to moderate selected objects plus all related objects.
    """
    opts = modeladmin.model._meta
    
    # If moderation is disabled..
    if not model_from_queue(modeladmin.model):
        return 0

    # Check that the user has required permission for the actual model.
    # To reset to pending status, change_perm is enough. For all else,
    # user need to have moderate_perm.
    if (
        (status == PENDING_STATUS and
            not modeladmin.has_change_permission(request)
        ) or 
        (status != PENDING_STATUS and
            not modeladmin.has_moderate_permission(request)
        )
    ):
        raise PermissionDenied

    # Approved objects can not further be moderated.
    queryset = queryset.exclude_approved()

    # After moderating objects in queryset, moderate related objects also
    q_count = queryset.count()

    # We want to use the status display rather than abbreviations in logs.
    status_display = STATUS_DICT[status]

    if q_count:
        #for obj in queryset:
            #message = 'Changed status from %s to %s.' % (
            #    obj.get_status_display(), status_display
            #)
            #modeladmin.log_moderation(request, obj, message)
            #me = MonitorEntry.objects.get_for_instance(obj)
        moderate_rel_objects(queryset, status, request.user)
    return q_count
        
def approve_selected(modeladmin, request, queryset):
    """ Default action to approve selected objects """
    ap_count = moderate_selected(modeladmin, request, queryset, APPROVED_STATUS)
    if ap_count:
        modeladmin.message_user(
            request,
            _("Successfully approved %(count)d %(items)s.") % {
                "count": ap_count,
                "items": model_ngettext(modeladmin.opts, ap_count)
            }
        )
    # Return None to display the change list page again.
    return None
approve_selected.short_description = ugettext_lazy(
    "Approve selected %(verbose_name_plural)s"
)

def challenge_selected(modeladmin, request, queryset):
    """ Default action to challenge selected objects """
    ch_count = moderate_selected(modeladmin, request, queryset, CHALLENGED_STATUS)
    if ch_count:
        modeladmin.message_user(
            request,
            _("Successfully challenged %(count)d %(items)s.") % {
                "count": ch_count,
                "items": model_ngettext(modeladmin.opts, ch_count)
            }
        )
    # Return None to display the change list page again.
    return None
challenge_selected.short_description = ugettext_lazy(
    "Challenge selected %(verbose_name_plural)s"
)

def reset_to_pending(modeladmin, request, queryset):
    """ Default action to reset selected object's status to pending """
    ip_count = moderate_selected(modeladmin, request, queryset, PENDING_STATUS)
    if ip_count:
        modeladmin.message_user(
            request,
            _("Successfully reset status of %(count)d %(items)s.") % {
                'count': ip_count,
                'items': model_ngettext(modeladmin.opts, ip_count)
            }
        )
    return None
reset_to_pending.short_description = ugettext_lazy(
    "Reset selected %(verbose_name_plural)s to pending"
)

