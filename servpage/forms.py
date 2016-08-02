from django.forms import ModelForm,Textarea
from django import forms
from ftft.servpage.models import splitalbum

class splitalbumform(ModelForm):
	titolo = forms.CharField(error_messages = {'required':'Inserire Un Titolo'})
	slot = forms.ChoiceField(choices=((str(y), y) for y in range(4,21)))
	slotpergroup = forms.ChoiceField(choices=((str(x), x) for x in range(1,5)), label="Max slot per gruppo")
	copie = forms.IntegerField(min_value=0,max_value=1000)
	class Meta:
	        model = splitalbum
	        fields = ['titolo','descrizione','slot','slotpergroup','copie']
       		widgets = {'descrizione': Textarea(attrs={'cols':'23','rows':'9','maxlength':'300'})}
