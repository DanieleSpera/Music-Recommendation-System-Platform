from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from datetime import datetime
from ftft.canzoni.models import canzone, deposito
from ftft.accountsys.models import Drinkers
from ftft.canzoni.forms import formdeposito


# Deposito
def depsong(request):
	c = {}
	idcanz = request.POST.get('idcanz')
	utente = User.objects.get(id=request.user.id)
	dett = Drinkers.objects.get(user=request.user.id)
	if utente.first_name and utente.last_name and dett.documento and dett.numerodoc and dett.birthday and dett.luogonascita:
		c = {}
		'''canzone - user - licenza - autori - data'''
		form = formdeposito()
		c.update({'form':form })
		c.update({'selected':idcanz })
		c.update({'page':"pageuno" })
	else:
		c.update({'page':"fail" })
	return render_to_response('moduli/deposito.html',c)

def depconfirm(request):
	c = {}
	utente = User.objects.get(id=request.user.id)
	idcanz = request.POST.get('selected')
	canz = canzone.objects.get(id=idcanz)
	c.update({'dett' : Drinkers.objects.get(user=utente)})

	#Mostra licenza
	if request.POST.get('show'):
		dep=deposito.objects.get(canzone=canz)
		c.update({'dep' : dep})
		c.update({'page' : "show"})

		return render_to_response('moduli/deposito.html',c)


	autori = request.POST.get('aut')
	data = datetime.now()
	c.update({'canz' : canz})
	c.update({'autori' : autori})
	c.update({'utente' : utente})
	c.update({'dett' : Drinkers.objects.get(user=request.user.id)})
	c.update({'time': data})


	if not request.POST.get('user'):
		c.update({'page':"riepilogo" })
	else:
		lic = canz.licenza
		dep=deposito(canzone=canz,user=utente,licenza=lic,autori=autori,data=data)
		dep.save()
		c.update({'page':"conferma" })

	return render_to_response('moduli/deposito.html',c)
