from django.db import models
import subprocess, threading
import os, glob
import string
from webgui.crontab import *

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
"""
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data


class Webradio(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)  # is the webradio selected to be played

    def __unicode__(self):
        return u'{0}'.format(self.name)
    

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
        split_url = string.split(url, ".")
        size_tab = len(split_url)
        extension = split_url[size_tab-1]
        command = self.getthegoodcommand(extension)

        subprocess.Popen(command+radio.url, shell=True)

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


class BackupMP3(models.Model):
    mp3file = ContentTypeRestrictedFileField(upload_to='backup_mp3',
                                             content_types=['audio/mp3',
                                                            'audio/mpeg'],
                                             max_upload_size=214958080
                                             )


def _backup_exist():
    path = "backup_mp3/*"
    filelist = glob.glob(path)
    if filelist:
        return True
    return False