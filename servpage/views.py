from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext

from django.contrib.auth.models import User
from ftft.accountsys.models import Rate, Playlist
from ftft.gruppi.models import gruppo

from ftft.search.views import pearson

from ftft.servpage.models import tutorial,splitalbum, tutorialform
from ftft.servpage.forms import splitalbumform


# Create your views here.

# INSERISCI TUTORIAL
def instutorial(request):
    c = {}
    c.update(csrf(request))
    form = tutorialform
    if request.method =='POST':
        formset=form(request.POST,request.FILES)
        if formset.is_valid():
            formset.save()
        # ... view code here
        ok ="Tutorial Inserito"
        c.update({'ok':ok })
        return render_to_response('back/insform.html',c)
    form = tutorialform()
    c.update({'form':form })
    return render_to_response('back/insform.html',c)

def showtutorial(request):
    tutorials= tutorial.objects.all()
    return render_to_response('tutorial.html',{'tutorials':tutorials})

# SPLIT ALBUM /25 intero/
def splitouser(spitcdid,*users):

	# UTENTI Passati-----------------------------------------------------
	utenti= users

	# UTENTE BASE--------------------------------------------------
	# Per ogni utente estrai lista gruppi e valutazioni
	for u in utenti:
		utentedict = Rate.objects.values_list('gruppo', 'valutazione').filter(user=u)
		utentegruppi = [i[0] for i in utentedict]
		utentevoti = [i[1] for i in utentedict]

		# UTENTE TEST----------------------------------------------------
		# II livello --- Per ogni utente estrai lista gruppi e valutazioni e calcola indice perarson con tutti gli utenti-test candidati

		# Estrai lista utenti test
		utentitest = Rate.objects.values_list('user',flat=True).filter(gruppo__in=utentegruppi).distinct().exclude(id=u)#MODIFICA escludi tutti gli Utenti-suggeriti all inizio
		# III Livello
		for test in utentitest:
			testdict = Rate.objects.values_list('gruppo', 'valutazione').filter(user=test)
			# gruppi utente base -> len = quantita gruppi votati
			testgruppi = [i[0] for i in testdict]
			testrate = [i[1] for i in testdict]

			# IV Livello componi la lista adatta al confronto
			testvoti = []
			for g in utentegruppi:
				if g in testgruppi:
					indice = testgruppi.index(g)
					voto = testrate[indice]
					testvoti.append(voto)
				else:
					testvoti.append(0)

			# CONFRONTO----------------------------------------------
			indicepearson = pearson(utentevoti ,testvoti)
			# Filtro indice Pearson
			splitcd = splitalbum.objects.get(id=spitcdid)
			if indicepearson > 0.5:
				splitcd.intrestusr.add(test)


# SPLIT ALBUM
def splitcd(request):
	c = {}
	c.update(csrf(request))
    #context = RequestContext(request)

	# ESTRAI SPLIT DISPONIBILI
	split = splitalbum.objects.all()
	c.update({'split':split })

	# ESTRAI gruppi dell'utente e split gia riempiti
	split =  splitalbum.objects.all()

	# INSERISCI SPLIT
	if request.method == 'POST':
		form=splitalbumform(request.POST)
		if form.is_valid():
			new = form.save(commit=False)
			new.user=request.user
			new.save()
			return HttpResponseRedirect('/splitcd')
		else:
  			print (form.errors)
	else:
		form = splitalbumform()
		c.update({'form':form })
	return render_to_response( 'split.html',c,context_instance=RequestContext(request))

# INSERIMENTO
def splitins(request):
	c = {}
	canz = request.POST.get('canzoni')
	album = request.POST.get('album')
	grup = gruppo.objects.filter(canzone=canz)
	us= User.objects.filter(rate__in=Rate.objects.filter(valutazione__gt=3).filter(gruppo=grup))
	usp = User.objects.filter(playlist__in=Playlist.objects.filter(canzone=canz))
	usd = us | usp
	splitcd = splitalbum.objects.get(id=album)
	splitcd.canzoni.add(canz)
	for u in usd:
		splitcd.intrestusr.add(u)
	c.update({'cd':splitcd })
	splitouser(splitcd.id,usd)
	return render_to_response( 'moduli/rendersplit.html',c,context_instance=RequestContext(request))


def faq(request):
    c = {}
    return render_to_response( 'faq.html', RequestContext(request))