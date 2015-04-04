#!/usr/bin/env python
import os
import sys
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'piclodio.settings'
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.append(SITE_ROOT)
application = get_wsgi_application()
from webgui.models import *

print SITE_ROOT
# Getting Alarmclock object from database
acid = sys.argv[1]
ac = Alarmclock.objects.get(id=acid)

# Check if autosnooze activated
snooze = ac.snooze
if snooze != 0:
    cmd = 'echo "sudo /usr/bin/killall mplayer" |sudo /usr/bin/at "now +'+str(snooze)+' minute"'
    p = subprocess.Popen(cmd, shell=True)

# Play the radio
player = Player()
radio = ac.webradio
player.play(radio)
