from django.forms import ModelForm
from ftft.canzoni.models import canzone
from django import forms




class songform(ModelForm):
	gruppo = forms.CharField()
	genere = forms.CharField()

	def __init__(self, *args, **kwargs):
	        super(songform, self).__init__(*args, **kwargs)
	        # Making name required
	        self.fields['moood'].label = 'Mood'

	class Meta:
	        model = canzone
	        exclude = ["contenuto"]
