from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.contrib import auth
from django.contrib.auth import authenticate

from django.contrib.auth.models import User
from ftft.accountsys.forms import RecMod,CompletRec,SetMode,ChangeAvatar, LoginForm
from ftft.accountsys.models import Drinkers,Topten,Playlist,Rate, Ascolti
from ftft.gruppi.models import famusartist, gruppo, influence, gruppoform
from ftft.canzoni.models import canzone
from ftft.testing.models import Compilation
from ftft.search.views import searchbyplaylist, selectfromtopten, BandUserSuggestion


from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from datetime import datetime

#0 Test
def hello(request):
    return HttpResponse("Hello world")


#1 Home - Redirect profile
def home(request):
    c = {}
    if request.user.is_authenticated():
        c.update({'user' : request.user, 'request' : request})
        return HttpResponseRedirect('/profile')
    else:
        return render_to_response('index.html',c)

# 3 Registration User
def register_user(request):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/profile')
        if request.method == 'POST':
            form = RecMod(request.POST)
            if form.is_valid():
                if form.cleaned_data['password']:
                    user = User.objects.create_user(username=form.cleaned_data['username'], email = form.cleaned_data['email'], password = form.cleaned_data['password'],first_name = form.cleaned_data['first_name'],last_name = form.cleaned_data['last_name'])
                    if user is not None:
                        '''user.save()'''
                    drinker = Drinkers(user=user,birthday="1984-01-01",sesso=form.cleaned_data['sesso'],mailactive = 'True',ricactive = 'True')
                    drinker.save()
                    user.save()
                    user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                    auth.login(request, user)
                    return HttpResponseRedirect('/accounts/cprofile/')
                else:
                    raise "problema"
            else:
                return render_to_response('account/register.html', {'form': form}, context_instance=RequestContext(request))
        else:
            ''' user is not submitting the form, show them a blank registration form '''
            form = RecMod()
            context = {'form': form}
            return render_to_response('account/register.html', context, context_instance=RequestContext(request))

# 4 Complete Registration
@login_required
def cprofile(request):
    c = {}
    c.update(csrf(request))
    form = CompletRec
    if request.method =='POST':
        formcp=form(request.POST,request.FILES)
        if formcp.is_valid():
            drinkers = Drinkers.objects.get(user=request.user.id)
            drinkers.mailactive=request.POST.get('mailactive')
            drinkers.ricactive=request.POST.get('ricactive')
            drinkers.provincia=request.POST.get('provincia')
            drinkers.indirizzo=request.POST.get('indirizzo')

            if request.POST.get('documento') is not None:
                drinkers.documento=request.POST.get('documento')
            else:
                drinkers.documento='NULL'

            if request.POST.get('numerodoc') is not None:
                drinkers.numerodoc=request.POST.get('numerodoc')
            else:
                drinkers.numerodoc='NULL'

            if request.POST.get('birthday') is not None and request.POST.get('birthday') != '':
                birth = datetime.strptime(request.POST.get('birthday'), '%d/%m/%Y').strftime('%Y-%m-%d')
                drinkers.birthday=birth
            if request.POST.get('luogonascita') is not None:
                drinkers.luogonascita=request.POST.get('luogonascita')
            drinkers.save()
            return HttpResponseRedirect('/profile')
        else:
            return HttpResponseRedirect('/profile')
    else:
        form = CompletRec()
        context = {'form': form}
        return render_to_response('account/completeprofile.html', context, context_instance=RequestContext(request))

# 6 Profile   formset.referente.add(user)
@login_required
def profile(request):
	if request.user.is_authenticated():
		# Inserimento gruppi
		if request.POST.get('forminserimentogruppo'):
			formset = gruppoform (request.POST,request.FILES)
			if formset.is_valid():
				grup = formset.save()
				user = request.user.id
				grup.referente.add(user)
				idlink = str(grup.id)
				return HttpResponseRedirect('/modgruppo/'+idlink)
			else:
				return HttpResponseRedirect('/setting')
		# Cambio immagine profilo
		if request.POST.get('forminserimentoimmagine'):
			formset = ChangeAvatar(request.POST,request.FILES)
			if formset.is_valid():
				drinkers = Drinkers.objects.get(user=request.user.id)
				drinkers.avatar = request.FILES['avatar']
				drinkers.save()

				return HttpResponseRedirect('/profile')
			else:
				return HttpResponseRedirect('/setting')
		else:
			# Estrapolazione informazioni user
			dati = Drinkers.objects.get(user=request.user.id)
			gruppi = gruppo.objects.filter(referente=request.user.id)
			insgrupform = gruppoform()
			imageprofile = ChangeAvatar()
			context = {'dati':dati,'insgrupform':insgrupform,'imgprofile':imageprofile, 'gruppi':gruppi,'pag':'profile'}
			# Estrapolazione Top ten
			topten = Topten.objects.filter(user=request.user.id)
			toptenpos = Topten.objects.values_list('posizione',flat=True).filter(user=request.user.id)
			position=[i+1 for i in range(10)]
			context.update({'position':position,'topten':topten,'toptenpos':toptenpos})
			# Estrapolazione play list
			playlist =  canzone.objects.filter(playlist=Playlist.objects.filter(user=request.user.id))
			# Ricerca by playlist
			canzoni = searchbyplaylist(request.user.id)
			canzoniontop = selectfromtopten(topten,request.user.id)
			canzoni.extend(canzoniontop)# append b to a
			gruppisuggonsugg = BandUserSuggestion(request.user.id)
			gruppisuggontop = gruppo.objects.filter(canzone__in=canzoniontop).distinct()
			# gruppirate = SearchByRate(request.user.id) -> In BandUserSuggestion
			gruppisugg = list(set(gruppisuggonsugg) | set(gruppisuggontop))
			context.update({'playlist':playlist,'canzoni':canzoni,'gruppisugg':gruppisugg})
			return render_to_response('account/profile.html', context, context_instance=RequestContext(request))

# 2Login
def logacc(request):
    if request.user.is_authenticated():
            return HttpResponseRedirect('/profile')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect('/profile')
            else:
                return render_to_response('account/login.html', {'form': form}, context_instance=RequestContext(request))
        else:
            return render_to_response('account/login.html', {'form': form}, context_instance=RequestContext(request))
    else:
        ''' user is not submitting the form, show the login form '''
        form = LoginForm()
        context = {'form': form}
        return render_to_response('account/login.html', context, context_instance=RequestContext(request))

# 5 Setting Profile
@login_required
def setting(request):
    c = {}
    c.update(csrf(request))
    form = CompletRec
    if request.method =='POST':
        formcp=form(request.POST,request.FILES)
        if formcp.is_valid():
            drinkers = Drinkers.objects.get(user=request.user.id)
            if request.POST.get('mailactive') is not None:
                drinkers.mailactive=request.POST.get('mailactive')
            else:
	            drinkers.mailactive=False
            if request.POST.get('ricactive') is not None:
                drinkers.ricactive=request.POST.get('ricactive')
            else:
                drinkers.ricactive=False
            if request.POST.get('birthday') is not None:
                birth = datetime.strptime(request.POST.get('birthday'), '%d/%m/%Y').strftime('%Y-%m-%d')
                drinkers.birthday=birth
            if request.POST.get('luogonascita') is not None:
                drinkers.luogonascita=request.POST.get('luogonascita')
            if request.POST.get('provincia') is not None:
                drinkers.provincia=request.POST.get('provincia')
            if request.POST.get('indirizzo') is not None:
                drinkers.indirizzo=request.POST.get('indirizzo')
            if request.POST.get('documento') is not None:
                drinkers.documento=request.POST.get('documento')
            if request.POST.get('numerodoc') is not None:
                drinkers.numerodoc=request.POST.get('numerodoc')
                drinkers.save()

            user = request.user
            if request.POST.get('email') is not None:
                user.email=request.POST.get('email')
            if request.POST.get('first_name') is not None:
                user.first_name=request.POST.get('first_name')
            if request.POST.get('last_name') is not None:
                user.last_name=request.POST.get('last_name')
            user.save()

            return HttpResponseRedirect('/profile')
        else:
            return HttpResponseRedirect('/setting')
    else:
        user = request.user
        dati = Drinkers.objects.get(user=request.user.id)
        fform = SetMode(instance=request.user)
        form = CompletRec(instance=dati)
        context = {'form': form,'fform':fform}
        return render_to_response('account/setting.html', context, context_instance=RequestContext(request))

# 9 Ritorna gruppi famosi
@login_required
def getfartist(request):
    artisti = famusartist.objects.all
    pos = request.POST.get('pos')
    contenuto = {'artisti': artisti,'pos':pos}
    return render_to_response('moduli/showfartist.html', contenuto)

# 7 inserisci influenza
@login_required
def insinchart(request):
	if request.method == 'POST':
		pos = request.POST.get('pos')
		art = request.POST.get('art')
		tab = request.POST.get('tab')
		if tab=="top":
			us = request.POST.get('us')
			art = famusartist.objects.get(id=art)
			us = User.objects.get(id=us)
			if Topten.objects.filter(user=us).filter(artist=art):
				insert = Topten.objects.get(user=us,artist=art)
				insert.posizione = pos
				insert.save()
				return HttpResponse('Sostituito')
			if Topten.objects.filter(user=us).filter(posizione=pos):
				return HttpResponse('Posizione Mantenuta')
			else:
				insert = Topten(user=us,artist=art,posizione=pos)
				insert.save()
				return HttpResponse('Inserito')
	if tab=="inf":
		band = request.POST.get('us')
		art = famusartist.objects.get(id=art)
		band = gruppo.objects.get(id=band)
		if influence.objects.filter(gruppo=band).filter(artist=art):
			return HttpResponse('Err1')
		if influence.objects.filter(gruppo=band).filter(posizione=pos):
			return HttpResponse("Err2")
		else:
			insert = influence(gruppo=band,artist=art,posizione=pos)
			insert.save()
			return HttpResponse('Inserito')

# 8 Elimina Influenza
@login_required
def deleteinfluence(request):
		if request.method == 'POST':
			idb = request.POST.get('idb')
			pos = request.POST.get('pos')
			tab = request.POST.get('tab')
			if tab == "inf":
				delinfl = influence.objects.filter(gruppo=idb).filter(posizione=pos)
			if tab == "top":
				delinfl = Topten.objects.filter(user=idb).filter(posizione=pos)
			if tab == "play":
				delinfl = Playlist.objects.filter(user=idb).filter(canzone=pos)
			if tab == "group":
				delinfl = gruppo.objects.filter(id=pos)
			delinfl.delete()
			return HttpResponse("deleted")

#-------------------------------------------------------------------------------
# 1 Inserisci in Playlist
@login_required
def addplaylist(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user'))
        canz = canzone.objects.get(id=request.POST.get('canzone'))
        # controllo pre inserimento
        if Playlist.objects.filter(user=user).filter(canzone=canz):
            return HttpResponse('Err1')
        else:
            insert = Playlist(user=user,canzone=canz)
            insert.save()
            return HttpResponse('Inserito')

# 2 Inserisci in Playlist
@login_required
def rate(request):
    if request.method == 'POST':
        # conversione variabili
        user = User.objects.get(id=request.POST.get('user'))
        grup = gruppo.objects.get(id=request.POST.get('band'))
        valutazione = request.POST.get('rating')
        # controllo esistenza -> modifica
        if Rate.objects.filter(user=user).filter(gruppo=grup):
            for record in Rate.objects.filter(user=user).filter(gruppo=grup):
                record.valutazione=valutazione
                record.save()
            return HttpResponse('change')
	    # inserimento
        else:
            insert = Rate(user=user,gruppo=grup,valutazione=valutazione)
            insert.save()
            return HttpResponse('ricevuto')

# 3 Player Test
def playertest(request):
    canzoni = canzone.objects.filter(gruppo=1)
    var = {}
    var.update({'canzoni':canzoni})
    return render_to_response('playertest.html',var)

# 4 Registra ascolto
def recplay(request):
    if request.method == 'POST':
        canz = request.POST.get('idcanz')
        canz = canzone.objects.get(id=canz)

    if request.POST.get('user'):
        user = request.POST.get('user')
        user = User.objects.get(id=user)
        if Ascolti.objects.filter(user=user).filter(canzone=canz):
            ascolti = Ascolti.objects.get(user=user,canzone=canz)
            num = ascolti.nascolti + 1
            ascolti.nascolti = num
            ascolti.save()
            #conferma ascolto in test da cancellare finito il test
            asccomp = Compilation.objects.filter(user=user,canzone=canz)
            for asc in asccomp:
                asc.ascoltato = True
                asc.save()
        else:
            ascolti = Ascolti(user=user,canzone=canz,nascolti=1)
            ascolti.save()
            #conferma ascolto in test da cancellare finito il test
            asccomp = Compilation.objects.filter(user=user,canzone=canz)
            for asc in asccomp:
                asc.ascoltato = True
                asc.save()
    else:
        if Ascolti.objects.filter(user=None).filter(canzone=canz):
            ascolti = Ascolti.objects.filter(user=None).filter(canzone=canz)
            ascolti.nascolti = ascolti.nascolti + 1
            ascolti.save()
        else:
    	    ascolti = Ascolti(canzone=canz,nascolti=1)
    	    ascolti.save()

    return HttpResponse('hallo world')