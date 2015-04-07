#!/usr/bin/env python
import os
from os import path, getcwd
os.environ['DJANGO_SETTINGS_MODULE'] = 'piclodio.settings'
import sys
from django.core.wsgi import get_wsgi_application
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
    cmd = 'echo "sudo /usr/bin/killall mplayer" | sudo /usr/bin/at "now +' + str(snooze) + ' minute"'
    p = subprocess.Popen(cmd, shell=True)

# Program a check in 3 minutes
base_dir = os.path.dirname(path.abspath(__file__))
cmd = 'echo "bash ' + base_dir + '/checkRadioRunBackup.sh" ' + base_dir + '/backup_mp3/*.mp3 | sudo /usr/bin/at "now +3 minute"'
p = subprocess.Popen(cmd, shell=True)

# Play the radio
player = Player()
radio = ac.webradio
player.play(radio)
