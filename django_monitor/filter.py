from django.contrib.admin.filterspecs import ChoicesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django_monitor.conf import STATUS_DICT

class MonitorFilter(ChoicesFilterSpec):
    """
    A custom filterspec to enable filter by monitor-status.
    Django development version has changes in store to break this!
    """
    def __init__(
        self, f, request, params, model, model_admin, field_path = None
    ):
        ChoicesFilterSpec.__init__(
            self, f, request, params, model, model_admin, field_path
        )
        self.lookup_kwarg = 'status'
        # usually, lookup_vals are extracted from request.GET. But we have
        # intentionally removed ``status`` from GET before.
        # (Have a look at ``django_monitor.admin.MonitorAdmin.queryset`` to
        # know why). So we'll apply regex over the url:
        import re
        status_matches = re.findall(
            r'status=(?P<status>%s)' % '|'.join(STATUS_DICT.keys()),
            request.get_full_path()
        )
        self.lookup_val = status_matches[0] if status_matches else None
        self.lookup_choices = STATUS_DICT.keys()
        
    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }
        for val in self.lookup_choices:
            yield {
                'selected': smart_unicode(val) == self.lookup_val,
                'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                'display': STATUS_DICT[val]
            }

    def title(self):
        """ The title displayed above the filter"""
        return _("Moderation status")

