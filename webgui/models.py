from django.db import models
import subprocess, threading
import os
import string
from webgui.crontab import *



class Webradio(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)  # is the webradio selected to be played
    

class Alarmclock(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    label = models.CharField(max_length=100)
    hour = models.IntegerField(blank=True)
    minute = models.IntegerField(blank=True)
    period = models.CharField(max_length=100)    # cron syntax dow (day of week)
    active = models.BooleanField(default=True)
    snooze = models.IntegerField(blank=True)
    webradio = models.ForeignKey(Webradio)

    def enable(self):
        """
        enable The alarm clock. Set it into the crontab
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        cron = Crontab()
        cron.minute = self.minute
        cron.hour = self.hour
        cron.period = self.period
        cron.comment = "piclodio "+str(self.id)
        cron.command = "env DISPLAY=:0.0 python "+base_dir+"/runWebRadio.py "+str(self.id)
        cron.create()

    def disable(self):
        """
        disable the alarm clock. remove it from the crontab
        """
        cron = Crontab()
        cron.comment = "piclodio "+str(self.id)
        cron.remove()


class Player():
    """
    Class to play music with mplayer
    """
    def __init__(self):
        self.status = self.isStarted()

    def play(self, radio):
        # kill process if already running
        if self.isStarted():
            self.stop()

        url = radio.url  # get the url
        splitUrl =string.split(url, ".")
        sizeTab= len(splitUrl)
        extension=splitUrl[sizeTab-1]
        command= self.getthegoodcommand(extension)

        #p = subprocess.Popen(command+radio.url, shell=True)
        player_thread = PlayerThread(command+radio.url)
        player_thread.run(timeout=3)

    def stop(self):
        """
        Kill mplayer process
        """
        p = subprocess.Popen("sudo killall mplayer", shell=True)
        p.communicate()
   
    def getthegoodcommand(self, extension):
        """
        switch extension, start mplay differently
        """
        return {
            'asx': "sudo /usr/bin/mplayer -playlist "

        }.get(extension, "sudo /usr/bin/mplayer ")  # default is mplayer

    def isStarted(self):
            # check number of process
            p = subprocess.Popen("sudo pgrep mplayer", stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            if output == "":
                    return False
            else:
                    return True


class PlayerThread(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout=0):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        try:
            if not thread.is_alive():
                print 'Mplayer not runing after timeout'
                self.process.terminate()
                thread.join()
        except OSError:
            print "Mplayer not runing after timeout. Start backup"
            player_thread = PlayerThread('mplayer -loop 0 backup.mp3')
            player_thread.run(timeout=3)

        print self.process.returncode