from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from ftft.accountsys.models import Drinkers

class RecMod(ModelForm):
    username    = forms.CharField(label=(u'Nome Utente'))
    email       = forms.EmailField(label=(u'Email'))
    password    = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    password1   = forms.CharField(label=(u'Verifica Password'), widget=forms.PasswordInput(render_value=False))
    first_name	= forms.CharField(label=(u'Nome'))
    last_name	= forms.CharField(label=(u'Cognome'))
    sesso		= forms.CharField(widget=forms.Select(choices=(("M","Maschio"),("F","Femmina"))))

    class Meta:
        model = Drinkers
        fields = ['username', 'email','password','password1']

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("Username in uso, selezionarne un altro.")

    def clean(self):
        password = self.cleaned_data.get('password', None)
        cpassword = self.cleaned_data.get('password1', None)
        if password == cpassword and password != '' and cpassword != '' :
            return self.cleaned_data
        raise forms.ValidationError("Controlla le password!")


class CompletRec(ModelForm):
    numerodoc	= forms.CharField(label=(u'Numero Documento'))
    mailactive = forms.BooleanField(required=False,initial='true',label='Mailinglist')
    ricactive = forms.BooleanField(required=False,initial='on',label='Voi ricevere cd Promo?')
    provincia = forms.CharField(max_length=200,required=False)
    indirizzo = forms.CharField (widget=forms.Textarea,required=False)
    birthday = forms.DateField(label=u'Data di Nascita (dd/mm/aaaa)', input_formats=['%d/%m/%Y', '%m/%d/%Y','%d-%m-%Y'], required=False, widget=forms.DateInput(format = '%d/%m/%Y'))
    luogonascita = forms.CharField(label=(u'Luogo di nascita'))

    class Meta:
        model = Drinkers
        fields = ['birthday','luogonascita','indirizzo','provincia','documento','numerodoc','mailactive','ricactive',]

class SetMode(ModelForm):
    email = forms.EmailField(label=(u'Email Address'))
    first_name	= forms.CharField(label=(u'Nome'))
    last_name	= forms.CharField(label=(u'Cognome'))

    class Meta:
        model = User
        fields = ['email','first_name','last_name']

class ChangeAvatar(ModelForm):
    class Meta:
        model = Drinkers
        fields = ['avatar']

class LoginForm(forms.Form):
        username        = forms.CharField(label=(u'User Name'))
        password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))