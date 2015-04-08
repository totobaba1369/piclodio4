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
import urllib

print SITE_ROOT
# Getting Alarmclock object from database
acid = sys.argv[1]
ac = Alarmclock.objects.get(id=acid)

# get base directory
base_dir = os.path.dirname(path.abspath(__file__))
# get player
player = Player()
# get url
radio = ac.webradio
mp3_backup = base_dir + '/backup_mp3/*.mp3'

# Check if autosnooze activated
if ac.snooze != 0:
    cmd = 'echo "sudo /usr/bin/killall mplayer" | sudo /usr/bin/at "now +' + str(ac.snooze) + ' minute"'
    p = subprocess.Popen(cmd, shell=True)

# check if URL is available
    try:
        http_code = urllib.urlopen(radio.url).getcode()
    except IOError:
        http_code = 0
    if http_code == 200:
        player.play(radio)
        # URl may be availlable, but no stream inside, so we check if mplayer is running
        # Program a check in 3 secondes
        cmd = 'sleep 3 ; bash ' + base_dir + '/checkRadioRunBackup.sh ' + mp3_backup
        print cmd
        subprocess.Popen(cmd, shell=True)
    else:
        # play backup MP3
        radio.url = mp3_backup
        player.play(radio)

