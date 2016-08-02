from django.forms import ModelForm
from ftft.gruppi.models import gruppo
from django import forms

class inserimento(ModelForm):
    class Meta:
        model = gruppo

class modgrupform(ModelForm):
    biografia	= forms.CharField(widget=forms.Textarea,required=False,label=u"Biografia")
    logo = forms.FileField(widget=forms.FileInput,help_text=" ")

    class Meta:
        model = gruppo
        exclude = ["referente","influenze"]
