from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User


# Create your models here.

def validate_file_extension(value):
    if not value.name.endswith(('.png','.jpg','.jpeg','.gif')):
         raise forms.ValidationError(u'Error message')

class famusartist(models.Model):
    nome = models.CharField(max_length=50)
    genere = models.CharField(max_length=50)

    def __str__(self):
        return u"%s" %(self.nome)

class gruppo(models.Model):
    referente = models.ManyToManyField(User)
    nome = models.CharField(max_length=50)
    genere = models.CharField(max_length=50)
    logo = models.FileField(upload_to='logogruppi',validators=[validate_file_extension],blank=True,null=True)
    biografia = models.TextField()
    influenze = models.ManyToManyField(famusartist, through='influence')

    def __unicode__(self):
        return u"%s" %(self.nome)
    class Meta:
        verbose_name_plural="Gruppi"


class influence(models.Model):
    gruppo = models.ForeignKey(gruppo)
    artist = models.ForeignKey(famusartist)
    posizione = models.IntegerField()

    def __str__(self):
        return u"%s-%s->%s" %(self.artist,self.gruppo.nome,self.posizione)



class gruppoform(ModelForm):

    class Meta:
        model = gruppo
        exclude = ['referente', 'influenze']

class famusartistform(ModelForm):

    class Meta:
        model = famusartist
