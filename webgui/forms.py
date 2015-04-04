from __future__ import unicode_literals
from django import forms
from webgui.models import Webradio, Alarmclock, BackupMP3
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.encoding import force_text


class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple.renderer):
    """
    Make day select horizontal
    """
    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<div id="{0}">', id_) if id_ else '<div>'
        output = [start_tag]
        for widget in self:
            output.append(format_html(u'<span>{0}</span>', force_text(widget)))
        output.append('</span></div>')
        return mark_safe('\n'.join(output))


class WebradioForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           min_length=2,
                           max_length=100,
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    url = forms.CharField(label="URL",
                          min_length=2,
                          max_length=100,
                          required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = Webradio
        fields = ['name', 'url', ]


class AlarmClockForm(forms.ModelForm):
    choice_hour = [(str(i), i) for i in range(0, 24)]
    choice_minute = [(str(i), i) for i in range(0, 60)]
    choice_snooze = [(str(i), i) for i in range(0, 120)]
    choice_period = [('1', 'Mon'),
                     ('2', 'Tue'),
                     ('3', 'Wed'),
                     ('4', 'Thu'),
                     ('5', 'Fri'),
                     ('6', 'Sat'),
                     ('0', 'Sun')]

    label = forms.CharField(label="Label",
                            min_length=2,
                            max_length=100,
                            required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    hour = forms.ChoiceField(label="Hour",
                             choices=choice_hour,
                             required=True,
                             widget=forms.Select(attrs={'class': 'form-control input-sm'}))

    minute = forms.ChoiceField(label="Minute",
                               choices=choice_minute,
                               required=True,
                               widget=forms.Select(attrs={'class': 'form-control input-sm'}))

    period = forms.MultipleChoiceField(label="Day of week",
                                       choices=choice_period,
                                       required=True,
                                       error_messages={'required': 'At least you must select one day'},
                                       widget=forms.CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))

    snooze = forms.ChoiceField(label="Auto stop",
                               choices=choice_snooze,
                               required=True,
                               widget=forms.Select(attrs={'class': 'form-control input-sm'}))

    webradio = forms.ModelChoiceField(queryset=Webradio.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = Alarmclock
        fields = ['label', 'hour', 'minute', 'period', 'snooze', 'webradio']


class BackupMP3Form(forms.ModelForm):
    mp3file = forms.FileField(label='MP3 backup file',
                              required=True)

    class Meta:
        model = BackupMP3
        fields = ['mp3file']