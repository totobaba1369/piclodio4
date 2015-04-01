#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from webgui.models import Webradio, Player, Alarmclock
from webgui.forms import WebradioForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import os
import subprocess
from time import strftime


def homepage(request):
    try:
        radio = Webradio.objects.get(selected=1)
    except Webradio.DoesNotExist:
        radio = None
    player = Player()
    listalarmclock = Alarmclock.objects.all()
    # clock
    clock = strftime("%H:%M:%S")
    return render(request, 'homepage.html', {'radio': radio,
                                             'player': player,
                                             'listalarmclock': listalarmclock,
                                             'clock': clock})


def webradio(request):
    listradio = Webradio.objects.all()
    return render(request, 'webradio.html', {'listradio': listradio})


def update_webradio(request, id_webradio):
    selected_webradio = get_object_or_404(Webradio, id=id_webradio)
    form = WebradioForm(request.POST or None, instance=selected_webradio)
    if form.is_valid():
        form.save()
        return redirect('webgui.views.webradio')

    return render(request, 'update_webradio.html', {'form': form, 'radio': selected_webradio})


def addwebradio(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = WebradioForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # save web radio
            form.instance.selected = False
            form.save()
            return redirect('webgui.views.webradio')
    else:
        form = WebradioForm()

    return render(request, 'addwebradio.html', {'form': form})


def delete_web_radio(request, id_radio):
    radio = Webradio.objects.get(id=id_radio)
    radio.delete()
    return redirect('webgui.views.webradio')


def options(request):
    script_path = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
    current_volume = subprocess.check_output([script_path, "--getLevel"])
    current_mute = subprocess.check_output([script_path, "--getSwitch"])
    return render(request, 'options.html', {'currentVolume': current_volume, 'currentMute': current_mute})


def debug(request):
    todisplay = 'hello world debug'
    return render(request, 'debug.html', {'todisplay': todisplay})


def play(request, id_radio):
    # get actual selected radio if exist
    try:
        selectedradio = Webradio.objects.get(selected=1)
        # unselect it
        selectedradio.selected = False
        selectedradio.save()
    except Webradio.DoesNotExist:
        pass
    
    # set the new selected radio
    radio = Webradio.objects.get(id=id_radio)
    radio.selected = True
    radio.save()
    player = Player()
    player.play(radio)

    return redirect('webgui.views.homepage')


def stop(request):
    player = Player()
    player.stop()
    return redirect('webgui.views.homepage')
    

def alarmclock(request):
    list_alarm = Alarmclock.objects.all()
    return render(request, 'alarmclock.html', {'listAlarm': list_alarm})


def activeAlarmClock(request, id):
    alarmclock = Alarmclock.objects.get(id=id)
    if not alarmclock.active:
        alarmclock.active = True
        alarmclock.enable()
    else:
        alarmclock.active = False
        alarmclock.disable()
        
    alarmclock.save()
    return redirect('webgui.views.alarmclock')


@csrf_exempt 
def addalarmclock(request):
    if request.method == 'POST':
        label = request.POST['label']
        hour = request.POST['hour']
        minute = request.POST['minute']
        snooze = request.POST['snooze']
        id_webradio = request.POST['webradio']
        dayofweek = request.POST['dayofweek']
        
        # check if label not empty and days selected
        if label == "" or dayofweek == "":
            json_data = json.dumps({"HTTPRESPONSE": "error"})
            return HttpResponse(json_data, mimetype="application/json")
        
        # save object in database
        alarmclock = Alarmclock()
        alarmclock.label = label
        alarmclock.hour = hour
        alarmclock.minute = minute
        alarmclock.period = dayofweek
        alarmclock.snooze = snooze
        webradio = Webradio.objects.get(id=id_webradio)
        alarmclock.webradio = webradio
        alarmclock.active = True
        alarmclock.save()
        
        # set the cron
        alarmclock = Alarmclock.objects.latest('id')
        alarmclock.enable()

        # return the base URL of current instance
        url = request.build_absolute_uri('alarmclock')

        json_data = json.dumps({"HTTPRESPONSE":url})
        return HttpResponse(json_data, mimetype="application/json")
    
    else:  # not post, show the form
        listradio = Webradio.objects.all()
        return render(request, 'addalarmclock.html', {'rangeHour': range(24),
                                                      'rangeMinute': range(60),
                                                      'rangeSnooze': range(121),
                                                      'listradio': listradio})


def deleteAlarmClock(request, id_alarmclock):
    target_alarmclock = Alarmclock.objects.get(id=id_alarmclock)
    target_alarmclock.disable()
    target_alarmclock.delete()
    return redirect('webgui.views.alarmclock')


def volumeup(request, count):
    script_path = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
    subprocess.call([script_path, "--up", count])
    return redirect('webgui.views.options')


def volumedown(request, count):
    script_path = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
    subprocess.call([script_path, "--down", count])
    return redirect('webgui.views.options')


def volumeset(request, volume):
    script_path = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
    subprocess.call([script_path, "--setLevel", volume])
    return redirect('webgui.views.options')


def volumetmute(request):
    script_path = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
    subprocess.call([script_path, "--toggleSwitch"])
    return redirect('webgui.views.options')
