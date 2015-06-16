import sys, os

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'thewulf'))
os.environ['DJANGO_SETTINGS_MODULE'] = "thewulf.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
