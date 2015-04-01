from __future__ import unicode_literals
from django import forms
from webgui.models import Webradio



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