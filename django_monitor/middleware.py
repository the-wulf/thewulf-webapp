try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'monitor_user', None)

class MonitorMiddleware(object):
    def process_request(self, request):
        _thread_locals.monitor_user = getattr(request, 'user', None)
