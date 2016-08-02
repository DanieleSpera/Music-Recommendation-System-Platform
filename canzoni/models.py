from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from ftft.gruppi.models import gruppo
import os.path


# Create your models here.

def validate_file_extension(value):
    if not value.name.endswith('png'or'jpg'or'gif'or'jpeg'):
        raise ValidationError(u'Il file caricato non in formato immagine ')

def validate_file_audio(value):
    if not value.name.endswith('mp3'):
        raise ValidationError(u'Il file caricato non in formato un mp3')

class licenze(models.Model):
    titolo = models.CharField(max_length=150)
    icona = models.FileField(upload_to='static/servimg/licenze',validators=[validate_file_extension])
    descrizione = models.TextField()
    sintesi = models.URLField(blank=True)
    legalcode = models.URLField(blank=True)

    def __unicode__(self):
        return u"%s" %(self.titolo)
    class Meta:
        verbose_name_plural="Licenze"

class canzone(models.Model):
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

    titolo = models.CharField(max_length=150)
    contenuto = models.FileField(upload_to='canzoni',validators=[validate_file_audio])
    gruppo = models.ManyToManyField(gruppo)
    licenza = models.ForeignKey('licenze')
    moood = models.CharField(max_length=2,choices=mood_selezionabili,blank=True)

    def filename(self):
        return os.path.basename(self.contenuto.name)

    def __str__(self):
        return u"%s" %(self.titolo)

    def titolopuro(self):
        basename, extension = os.path.splitext(os.path.basename(self.contenuto.name))
        return basename

    class Meta:
        verbose_name_plural="canzoni"



class deposito(models.Model):
    canzone = models.ForeignKey('canzone')
    user = models.ForeignKey(User)
    licenza = models.ForeignKey('licenze')
    autori = models.TextField()
    data = models.DateField()

    def __unicode__(self):
        return u"%s" %(self.canzone)
    class Meta:
        verbose_name_plural="Depositi"
