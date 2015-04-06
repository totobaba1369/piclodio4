import os
import sys

path = '/usr/share/nginx/Piclodio2'
if path not in sys.path:
    sys.path.append(path)
    
    
os.environ['DJANGO_SETTINGS_MODULE'] = 'piclodio.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

