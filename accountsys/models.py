from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from ftft.gruppi.models import gruppo,famusartist
from ftft.canzoni.models import canzone

# Create your models here.

def validate_file_extension(value):
    if not value.name.endswith(('.png','.jpg','.jpeg','.gif')):
         raise forms.ValidationError(u'Error message')

class Drinkers(models.Model):
	tipidocu = (
		('Codice Fiscale', 'Codice Fiscale'),
		('Patente', 'Patente'),
	)

	user = models.OneToOneField(User)
	birthday=models.DateField(blank=True, null=True)
	luogonascita = models.CharField(max_length=200,blank=True)
	sesso=models.CharField(max_length=1)
	avatar= models.FileField(upload_to="profileimg",validators=[validate_file_extension])
	mailactive = models.BooleanField(default="true")
	ricactive = models.BooleanField(default="on")
	provincia = models.CharField(max_length=200,blank=True)
	indirizzo = models.TextField(blank=True)
	documento = models.CharField(max_length=50,choices=tipidocu,blank=True)
	numerodoc = models.CharField(max_length=200,blank=True)
	def __str__(self):
		return self.user.username

class ModifyProf(ModelForm):
    class Meta:
        model = Drinkers
        fields = ['mailactive','provincia','indirizzo','ricactive']

class Topten(models.Model):
	user = models.ForeignKey(User)
	artist = models.ForeignKey(famusartist)
	posizione = models.IntegerField()

	def __str__(self):
		return u"%s-%s -> %s" %(self.user,self.artist,self.posizione)

class Playlist(models.Model):
	user = models.ForeignKey(User)
	canzone = models.ForeignKey(canzone)

	def __str__(self):
		return u"%s-%s" %(self.user,self.canzone)

class Rate(models.Model):
	user = models.ForeignKey(User)
	gruppo = models.ForeignKey(gruppo)
	valutazione = models.IntegerField()

	def __str__(self):
		return u"%s-%s->%s" %(self.user,self.gruppo.nome,self.valutazione)

class Ascolti(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)
	canzone = models.ForeignKey(canzone)
	nascolti = models.IntegerField()

	def __str__(self):
		return u"%s-%s-%s" %(self.user,self.canzone,self.nascolti)