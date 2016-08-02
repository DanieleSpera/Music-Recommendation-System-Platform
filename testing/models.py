from django.db import models
from django.contrib.auth.models import User
from django import forms
from ftft.canzoni.models import canzone

# Create your models here.

def validate_file_extension(value):
    if not value.name.endswith(('.png','.jpg','.jpeg','.gif')):
         raise forms.ValidationError(u'Error message')

class Algoritmo(models.Model):
	algoritmo = models.CharField(max_length=50)

	def __str__(self):
		return u"%s-%s" %(self.id,self.algoritmo)

class Compilation(models.Model):
	user = models.ForeignKey(User)
	canzone = models.ForeignKey(canzone)
	algoritmo = models.ManyToManyField(Algoritmo)
	voto = models.IntegerField(blank=True)
	ascoltato = models.BooleanField(default=False)

	def __str__(self):
		return u"%s-%s" %(self.user,self.canzone)