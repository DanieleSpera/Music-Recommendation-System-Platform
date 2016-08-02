from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from ftft.canzoni.models import canzone

class tutorial(models.Model):
    titolo = models.CharField(max_length=50)
    descrizione = models.TextField(max_length=50)
    documento = models.FileField(upload_to='static/tutorial')

    def __unicode__(self):
        return u"%s" %(self.titolo)

class tutorialform(ModelForm):
    class Meta:
        model = tutorial
        fields = ['titolo', 'descrizione','documento']

class splitalbum (models.Model):
	user = models.ForeignKey(User)
	titolo = models.CharField(max_length=100,null=False,blank=False)
	descrizione = models.CharField(max_length=300)
	slot = models.PositiveIntegerField()
	slotpergroup = models.PositiveIntegerField()
	copie = models.PositiveIntegerField()
	canzoni = models.ManyToManyField(canzone,related_name="slotcanzoni",null=True,blank=True)
	data  = models.DateField(auto_now_add=True ,verbose_name="Data Inserimento")
	intrestusr = models.ManyToManyField(User,related_name="intric",null=True,blank=True)

