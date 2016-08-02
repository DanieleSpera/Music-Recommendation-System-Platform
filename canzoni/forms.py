from django import forms
from django.forms import ModelForm
from ftft.canzoni.models import deposito,canzone

class formdeposito(ModelForm):
    class Meta:
        model = deposito
        fields = ['autori']

class inscanz(ModelForm):
    mood_selezionabili = (
        ('1', 'Felice/Happy'),
        ('2', 'Eccitato'),
        ('3', 'Rabbioso'),
        ('4', 'Contento'),
        ('5', 'Tranquillo'),
        ('6', 'Agitato'),
        ('7', 'Rilassato'),
        ('8', 'Annoiato'),
        ('9', 'Pacifico'),
        ('10', 'Soporifero'),
        ('11', 'Triste/Malinconico'),
        ('12', 'Romantico'),
    )
    moood = forms.MultipleChoiceField(widget=forms.Select,choices=mood_selezionabili,label=u"Mood")

    class Meta:
        model = canzone
        exclude = ["gruppo"]