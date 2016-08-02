# Funzioni
import operator
# Moduli
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse


# Database
from ftft.canzoni.models import canzone, licenze
from ftft.gruppi.models import gruppo, influence, famusartist
from ftft.accountsys.models import Playlist, Rate, Topten

from ftft.search.forms import songform


# SEARCH BY TAG -----------------------------------------------------------------------------------------
def search(request):
	var = {}
	var.update(csrf(request))

	# form area
	form = songform()
	var.update({'form':form })

	'''if request.method =='POST':
	        formset=songform(request.POST)
		# searchbytag('nome','mood(id)','licenza(id)','genere','titolo')
		selezione = searchbytag(request.POST['gruppo'],request.POST['moood'],request.POST['licenza'],request.POST['genere'],request.POST['titolo'])
		var.update({'selezione':selezione})'''

	# estrai influenze
	influenze = famusartist.objects.order_by('nome')
	var.update({'influenze':influenze })

	return render_to_response('search.html',var,context_instance=RequestContext(request))


# LINK SEARCH BY TAG
def searchByTag(request):
	if request.method =='POST':
	    #formset=songform(request.POST)
	    selezione = searchbytag(request.POST['titolo'],request.POST['gruppo'],request.POST['licenza'],request.POST['moood'],request.POST['genere'])
        # searchbytag('titolo','gruppo','licenza(id)','mood(id)','genere')
	return render_to_response('moduli/searchresult.html',{'selezione':selezione})


# FUNCTION selezione by tag-----------------------------------------------------------------------------------------
def searchbytag(titolo,nomegruppo,licenza,mood,genere):
	if not titolo and not gruppo and not licenza and not mood and not genere:
		selezionetag = "no found"
	else:
		result = "no found"
		# 0 Apri Array ricerca

		# 2 Verifica se sono pieni
		if titolo:
			titolo= canzone.objects.filter(titolo__icontains=titolo)
			# 4 verifica che siano pieni
			if titolo:
				result = titolo

		if nomegruppo:
			nomegruppo= canzone.objects.filter(gruppo= gruppo.objects.filter(nome__icontains=nomegruppo))
			# 4 verifica che siano pieni
			if nomegruppo:
			# 5 se pieni inserisci in Array risultato
				if result == "no found":
					result = nomegruppo
				else:
					result = [i for i in result if i in nomegruppo]

		if licenza:
			licenza = canzone.objects.filter(licenza__in = licenze.objects.filter(id=licenza))
			# 4 verifica che siano pieni
			if licenza:
			# 5 se pieni inserisci in Array risultato
				if result == "no found":
					result = licenza
				else:
					result = [i for i in result if i in licenza]

		if mood:
			mood = canzone.objects.filter(moood=mood)
			# 4 verifica che siano pieni
			if mood:
			# 5 se pieni inserisci in Array risultato
				if result == "no found":
					result = mood
				else:
					result = [i for i in result if i in mood]

		if genere:
			genere = canzone.objects.filter(gruppo__in = gruppo.objects.filter(genere__icontains=genere))
			# 4 verifica che siano pieni
			if genere:
			# 5 se pieni inserisci in Array risultato
				if result == "no found":
					result = genere
				else:
					result = [i for i in result if i in genere]

	return result


# SEARCH BY DRAG & DROP -----------------------------------------------------------------------------------------
# LINK SEARCH BY DRAGDROP
def searchByDragDrop(request):
    if request.method =='POST':
        # Estrai dati da post, inserisci in lista associativa
        nvariabili= int((len(request.POST)-1)/2)
        lista = []
        for i in range(nvariabili):
            i=str(i)
            lista.append((request.POST['artista'+i],request.POST['peso'+i]))
        # Ordina la lista in base al peso
        lista = sorted(lista, key=lambda oggetto: oggetto[1], reverse=True)
        listart = [i[0] for i in lista]
        # Controlla se artisti presenti in database e inserisci id in lista-classifica
        hitlist = []
        for artista in listart:
            artsel = famusartist.objects.filter(nome__icontains=artista)
            if artsel:
                for a in artsel:
                    hitlist.append(a.id)
        # Selezione i primi 10
        topten = hitlist[:10]
        selezioneord = selectfromtopten(topten)
    return render_to_response('moduli/searchresult.html',{'selezione':selezioneord})

#WORK IN PROGRESS
# SEARCH BY TOP TEN -----------------------------------------------------------------------------------------
# LINK SEARCH BY TOP TEN
def searchByTopTen(request):
    if request.method =='POST':
        topten = []
        contatore = len(request.POST)-1
        for i in range(contatore):
            idg=request.POST['relations'+str(i+1)]
            grobj = famusartist.objects.filter(id=idg)
            topten.append(grobj)
        selezioneord = searchByTopOnBands(topten,"on")
        canzoni = frombandtosong(selezioneord)
    #return HttpResponse(selezioneord)
    return render_to_response('moduli/searchresult.html',{'selezione':canzoni})

def selectfromtopten(topten,usr=None):

    sbtb = searchByTopOnBands(topten)

    if usr:
        sbtu = searchByTopOnUser(topten,usr=usr)
    else:
        sbtu = searchByTopOnUser(topten)

    selezione= sbtb


    # aggiorna pesi e elimina duplicati
    for key,value in sbtu.items():
        if key not in selezione:
            selezione[key] = value
        else:
            selezione[key] += value

    # converti in tupla e ordina in base al peso
    selezionerisp = [(k,v) for k, v in selezione.items()]
    #selezionerisp = sorted(selezionerisp, reverse=True)
    selezionerisp = sorted(selezionerisp, key=lambda tup: tup[1], reverse=True)
    selezionerisp =  [i[0] for i in selezionerisp] # estrai la lista gruppi
    selezionerisp = frombandtosong(selezionerisp) # estrai canzoni consigliate

    return selezionerisp


# FUNCTION From Band List To Song List------------------------------------------------------------------------------
def frombandtosong(listagruppi):
    canzoni = [] # Apri lista che conterra risultati
    for g in listagruppi:
        #listacanz = canzone.objects.filter(gruppo=g)[:1]# decommentare on test
        listacanz = canzone.objects.filter(gruppo=g)
        if len(listacanz)>1:
            listacanz = listacanz.order_by('?')[1]
            '''for c in listacanz:
                if c not in canzoni:
                    canzoni.append(c)'''
            canzoni.append(listacanz)
        else:
            canzoni.append(listacanz)
    return canzoni

# FUNCTION From User To TopTen----------------------------------------------------------------------------------------
def fromusertotopten(userid):
	topten = Topten.objects.filter(user=userid).order_by('posizione')
	return topten

# FUNCTION Pearson Correlation-----------------------------------------------------------------------------------------
def pearson(x,y):
	n=len(x)
	vals=range(n)

	#regular sums
	sumx=sum([float(x[i]) for i in vals])
	sumy=sum([float(y[i]) for i in vals])

	#sum of the squares
	sumxSq=sum([x[i]**2.0 for i in vals])
	sumySq=sum([y[i]**2.0 for i in vals])

	#sum of the products
	pSum=sum([x[i]*y[i] for i in vals])

	#do pearson score
	num=pSum-(sumx*sumy/n)
	den = pow((sumxSq - pow(sumx, 2) / n) * (sumySq - pow(sumy, 2) / n), 0.5)
	if den==0:
		r = 1
	else:
		r=num/den
	return r

# Modifica return HttpResponse(list)#Controllo
# search by TOP-TEN ON BANDS-------------------------------------------------------------------------------------------------
# INPUT:1-10 SONGS LIST -> OUTPUT:BANDS  dict----------------------------------------------------------------------------------
def searchByTopOnBands(topten,case=None):
    startlist=topten
    x=10 #contatore pesi

    if case=="on":
        # RICERCA Per Pagina Ricerca
        gruppimod=dict() #dizionario dei gruppi e pesi
        for infl in startlist:#Per ogni influenza prendi i gruppi correlati
            gruppi = gruppo.objects.filter(influenze=infl)
            for g in gruppi: # Per ogni gruppo inserisci o calcola peso
                pesogruppo = influence.objects.get(artist=infl,gruppo=g)
                pesogruppo = 10
                if g in gruppimod:
                    gruppimod[g] += x * pesogruppo
                else:
                    gruppimod[g] = x * pesogruppo
            x = x-1

    else:
        # RICERCA Per Profilo
        gruppimod=dict() #dizionario dei gruppi e pesi
        for infl in startlist:#Per ogni influenza prendi i gruppi correlati
            try:
                gruppi = gruppo.objects.filter(influenze=infl.artist)
            except:
                gruppi = gruppo.objects.filter(influenze=infl)

            for g in gruppi: # Per ogni gruppo inserisci o calcola peso
                try:
                    pesogruppo = influence.objects.get(artist=infl.artist,gruppo=g)
                except:
                    pesogruppo = influence.objects.get(artist=infl,gruppo=g)
                pesogruppo = 11-pesogruppo.posizione
                if g in gruppimod:
                    gruppimod[g] += x * pesogruppo
                else:
                    gruppimod[g] = x * pesogruppo
            x = x-1
    return gruppimod


# Modifica
# SEARCH BY TOP-TEN ON USER--------------------------------------------------------------------------------------------
# INPUT:1-10 SONGS LIST -> OUTPUT:BANDS dict----------------------------------------------------------------------------------
def searchByTopOnUser(topten,usr=None):
    utentimod = dict() # dizionario degli utenti e pesi
    x = 10 	# contatore pesi
    for famusart in topten:
        try:
            campitop = Topten.objects.filter(artist=famusart.artist)
        except:
            campitop = Topten.objects.filter(artist=famusart)
        for campo in campitop:
            peso = 11 - campo.posizione
            if campo.user in utentimod:
                utentimod[campo.user] += x * peso
            else:
                if campo.user != usr:
                    utentimod[campo.user] = x * peso
        x = x-1

    #Estrapola 1risultato migliore, 2peggiore 3calcola media
    if len(utentimod) > 0 :
        mass_peso_ut = max([utentimod[i] for i in utentimod])
        minm_peso_ut = min([utentimod[i] for i in utentimod])
        med_peso = (mass_peso_ut + minm_peso_ut)/5
    else :
        mass_peso_ut=minm_peso_ut=med_peso=0
    #Verifica se utente loggato per eliminare risultati dopp
    # Ordina Risultati e inserisci in nuova lista i nomi utenti test
    # resultlist = list(sorted(utentimod, key=utentimod.__getitem__, reverse=True))
    # FINE ESTRAZIONE CLASSIFICA USER
    # Estrapola gruppi candidabili e inseriscigli/somma il peso utente
    Diz_gruppi_peso = dict() # Apri lista che conterra risultati
    for ut, peso in utentimod.items():
        if peso > med_peso:
            listagruppi = gruppo.objects.filter(rate=Rate.objects.filter(user=ut).filter(valutazione__gt=3))# Filtro valutazioni 3 / Togliere filtro 5 fuori dal test
            for c in listagruppi:
                if c in Diz_gruppi_peso:
                    Diz_gruppi_peso[c] += peso
                else:
                    Diz_gruppi_peso[c] = peso
    #Recupero peso massimo
    if len(Diz_gruppi_peso)>0:
        mass_peso_grup = max([Diz_gruppi_peso[i] for i in Diz_gruppi_peso])
    else:
        mass_peso_grup = 0
    #Normalizza sulla base del massimo peso-utente

    Diz_gruppi_peso = dict((grupp, int((peso*mass_peso_ut)/mass_peso_grup)) for (grupp, peso) in Diz_gruppi_peso.items())


    '''for grupp, peso in Diz_gruppi_peso.items():
        peso = (peso*mass_peso_ut)/mass_peso_grup'''
    return Diz_gruppi_peso

# EXTRACTOR PLAYLIST-------------------------------------------------------------------------------------------------
# INPUT:USER -> OUTPUT:PLAYLIST-----------------------------------------------------------------------------------------
def playlistextractor(iduser):
	# Prendi Utente
	user=User.objects.get(id=iduser)
	playlist=canzone.objects.filter(playlist=Playlist.objects.filter(user=user))
	return (playlist)

def fromsongtoband(idsong):
    song = canzone.objects.get(id=idsong)
    gruppi = []
    for art in song.gruppo.all():
        gruppi.append(art.id)
    return gruppi

# SEARCH BY PLAYLIST-------------------------------------------------------------------------------------------------
# INPUT:USER -> OUTPUT:SONGS-----------------------------------------------------------------------------------------
'''def searchbyplaylist(iduser):
	# Prendi Utente
	user=User.objects.get(id=iduser)
	playlist = canzone.objects.filter(playlist__user=iduser)
	insplaylist = set(playlist)
	# Seleziona utenti con almeno una canzone in comune
	usertest = User.objects.filter(playlist__canzone__in=playlist)# (canzone__in=playlist)?
	# Elimina doppi e user attivo
	usertest = list(set(usertest))
	if user in usertest:
		usertest.remove(user)
	# Inizializza dizionario play list
	songmod = dict()
	# Confronta insieme canzoni
	for test in usertest:
		playtest=canzone.objects.filter(playlist=Playlist.objects.filter(user=test))
		# Converti in Insieme
		insplaytest = set(playtest)
		intersezione = insplaylist & insplaytest
		peso = len(intersezione)
		if peso == 1:
			peso =1.5
		differenza = insplaytest - insplaylist
		for song in differenza:
			if song in songmod:
				songmod[song] += songmod[song] * peso
			else:
				songmod[song] = peso
	resultlist = list(sorted(songmod, key=songmod.__getitem__, reverse=True))
	# PER IL TEST COMMENTA LE SEGUENTI TRE LINEE e DECOMMENTA ULTIMA
	#resultlist = resultlist[:30]
	#shuffle(resultlist)
	#resultlist = resultlist[:10]
	resultlist = resultlist[:5]

	return (resultlist)
'''

def searchbyplaylist(iduser):
    #inizializzazione dati user
    #user_id=request.user.id
    user_id=iduser
    user_pl_id= []
    user_pl_art = []
    #inizializzazione user simili/matrici playlist
    usertest_id = []
    usertest_pl_id= []
    usertest_pl_art = []
    #inizializzazione artisti di cui calcolare peso similarita
    art_sel = []

    #estrazione playlist user
    user_pl=playlistextractor(user_id)
    #estrazione artisti
    for song in user_pl:
        user_pl_id.append(song.id)
        art = fromsongtoband(song.id)
        for a in art:
            if a not in user_pl_art:
                user_pl_art.append(a)

    #estrazione utenti con artisti in comune in playlist
    usertest = Playlist.objects.filter(canzone__in=user_pl)
    for us in usertest:
        if us.user.id not in usertest_id and us.user.id != user_id:
            usertest_id.append(us.user.id)

    #estrazioni playlist
    for u in usertest_id:
        #inizializzazione riga
        riga_pl= []
        riga_art=[]
        #estrazione playlist user
        pl=playlistextractor(u)
        #estrazione artisti
        for s in pl:
            riga_pl.append(s.id)
            art = fromsongtoband(s.id)
            for a in art:
                riga_art.append(a)
        usertest_pl_id.append(riga_pl)
        usertest_pl_art.append(riga_art)

    #selezione artisti per calcolo similarità
    for a in usertest_pl_art:
        for x in a:
            if x not in art_sel:
                art_sel.append([x])

    #inserici user_pl in matrice pl
    usertest_pl_art.append(user_pl_art)

    #costruisci matrice 1 e vettore1
    mat1=[]
    for pl in usertest_pl_art:
        riga = []
        for s in user_pl_art:
            if s in pl:
                riga.append(1)
            else:
                riga.append(0)
        mat1.append(riga)

    vec_mat1=[]
    for i in range(len(mat1)):
        for j in range(len(mat1[0])):
            if i == 0:
                vec_mat1.append(mat1[i][j])
            else:
                vec_mat1[j]=vec_mat1[j]+mat1[i][j]

    #calcola peso per ogni artista
    for art in art_sel:
        artist = art[0]
        #vettore presenze MatTest
        vec_art = []
        for pl in usertest_pl_art:
            if artist in pl:
                vec_art.append(1)
            else:
                vec_art.append(0)
        #somma vettore
        ris_test = 0
        for n in vec_art:
            ris_test = ris_test+n
        #matrice 2
        mat2=[]
        for j in range(len(vec_art)):
            riga = []
            for i in range(len(mat1[0])):
                x=mat1[j][i]*vec_art[j]
                riga.append(x)
            mat2.append(riga)
        #calcola somma colonne
        vec_mat2=[]
        for i in range(len(mat2)):
            for j in range(len(mat2[0])):
                if i == 0:
                    vec_mat2.append(mat1[i][j])
                else:
                    vec_mat2[j]=vec_mat2[j]+mat2[i][j]
        simset = 0
        for i in range(len(vec_mat1)):
            sim = float( vec_mat2[i]/ float( (ris_test*vec_mat1[i])**0.5 ) )
            simset = simset + sim

        #appendi peso al relativo gruppo
        indice = art_sel.index(art)
        art_sel[indice].append(simset)

    #-----------Valutazione canzone
    #seleziona canzoni da valutare
    canz_sel=[]
    for canz in usertest_pl_id:
        for c in canz:
            if c not in canz_sel and c not in user_pl_id:
                canz_sel.append(c)

    lista_ris=[]
    for canz in canz_sel:
        #conta
        c_song = 0
        for pl in usertest_pl_id:
            if canz in pl:
                c_song += 1
        #recupera gruppo
        art = fromsongtoband(canz)
        #recupera pesi e calcola media
        pesi = []
        for a in art:
            for ris in art_sel:
                if ris[0] == a:
                    peso = ris[1]
                    pesi.append(peso)
        cont = 0
        for p in pesi:
            cont = cont + p
        peso_def = cont/len(pesi)
        #calcola peso c_song * peso
        peso_canz= c_song * peso_def
        #appendi in lista
        lista_ris.append([canz,peso_canz])

    lista_ris = sorted(lista_ris,key=lambda x: x[1],reverse=True)

    #seleziona i primi 5
    lista_ris = lista_ris[:5]

    #recupera oggetto canzoni
    resultlist = []
    for c in lista_ris:
        canz = canzone.objects.get(id=c[0])
        resultlist.append(canz)
    #return HttpResponse(resultlist)
    return (resultlist)

# SEARCH BY RATE-------------------------------------------------------------------------------------------------
# INPUT:USER -> PLAYLIST -> PEARSON/USER -> OUTPUT: BANDS dict------------------------------------------------------------
def searchByRate(userid):
    user = User.objects.get(id=userid)
    # 1) Recupera valutazioni espresse dall'utente
    votiuser= Rate.objects.filter(user=user, valutazione__gte=3).reverse()
    '''if votiuser.count() > 5:
        votiuser= list(votiuser[:5])'''# 5 Restrizione per TEST
    banduser = dict()
    # Allestisci dizionario user gruppo,voto
    for v in votiuser:
        banduser[v.gruppo] = v.valutazione
    # 2) Recupera utenti con valutazione gruppi in comune(escludi utente base)
    usertest=User.objects.filter(rate=Rate.objects.filter(gruppo=gruppo.objects.filter(rate=votiuser))).distinct().exclude(id=user.id)

    # 3) Calcola l'indice di PEARSON
    classificaindici = dict()
    for u in usertest:
        bandtest = dict()
        for g in votiuser:
            if Rate.objects.filter(user=u).filter(gruppo=g.gruppo):
                testval=Rate.objects.get(id=Rate.objects.filter(user=u).filter(gruppo=g.gruppo))
                bandtest[testval.gruppo] = testval.valutazione
            else:
                bandtest[g.gruppo] = 0
        indicepearson = pearson(list(banduser.values()),list(bandtest.values()))
        classificaindici[u] = indicepearson

    #FILTRO
	# Filtra i piu alti di 0,75 abbassa la soglia in caso di nessun risultato
    soglia = 1
    numeroris = 0
    indicifiltrati = dict()
    while numeroris < 2 and soglia != 0:
        indicifiltrati = {k: v for k, v in classificaindici.items() if v > soglia}
        soglia = soglia - 0.25
        numeroris = len(indicifiltrati)

    '''indicifiltrati = {k: v for k, v in classificaindici.items() if v == 1}
    if len(indicifiltrati) == 0:
        indicifiltrati = {k: v for k, v in classificaindici.items() if v > 0}'''
    # Estrai una lista di utenti ordinati
    utentisuggeriti = sorted(indicifiltrati, key=indicifiltrati.__getitem__, reverse=True)

    # 3) Ricava e seleziona relativi gruppi con valutazione > 3
    gruppisuggeriti = dict()
    for s in utentisuggeriti:
        gruppivotati = gruppo.objects.filter(rate=Rate.objects.filter(user=s).filter(valutazione__gte=3))
        # Insieme utente base
        insut = set (gruppo.objects.filter(rate=votiuser))
        instest = set (gruppivotati)
        inssugg= instest-insut
        for g in inssugg:
            rate = Rate.objects.get(id=Rate.objects.filter(user=s).filter(gruppo=g))
            if g in gruppisuggeriti:
                gruppisuggeriti[g]  += gruppisuggeriti[g]  + rate.valutazione
            else:
                gruppisuggeriti[g] = rate.valutazione
    return (gruppisuggeriti)

#Filtro gruppi dell'utente e indesiderati
def negGrup(userid):
	filtro = gruppo.objects.filter(referente=User.objects.get(id=userid))
	return filtro

def BandUserSuggestion(userid):
	# prendi utente e top ten per iniziare le ricerche
	user=userid
	topten = fromusertotopten(user)

	# ricerca peri diversi metodi
	sbr = searchByRate(user)
	sbtb = searchByTopOnBands(topten)
	sbtu = searchByTopOnUser(topten)

	# popola il dizionario e pesa in base al numero di successi
	gruppi = dict()
	for g in sbr:
		gruppi[g] = 1

	for g in sbtb:
		if g in gruppi:
			gruppi[g]  += (gruppi[g]  + 1)
		else:
			gruppi[g] = 1

	for g in sbtu:
		if g in gruppi:
			gruppi[g]  += (gruppi[g]  + 1)
		else:
			gruppi[g] = 1

	filtrogruppi = negGrup(userid)
	for f in filtrogruppi:
		if f in gruppi:
			del gruppi[f]
	gruppi= sorted(gruppi, key=gruppi.__getitem__,reverse=True)[:20]
	# COMMENTARE PROSSIMA RIGA DURANTE TEST
	#shuffle(gruppi)
	gruppi = (gruppi)[:10]
	return gruppi

## ALGORITMI CORRELAZIONE DA UTENTI
# Prende id 2 user (user,canzone per predizione su gruppo) e ne calcola l'indice di correlazione di Pearson
def pearsonfromuser(usera,userb):
    recorda = Rate.objects.filter(user__id=usera)
    votia = []
    votib = []
    for v in recorda:
        votia.append(v.valutazione)
        try:
            valb = Rate.objects.get(user__id=userb,gruppo=v.gruppo)
            votib.append(valb.valutazione)
        except:
             votib.append(0)
    indice = pearson(votia,votib)

    return (indice)

#Indice somiglianza (user,canzone)
def onbandfromuser(user,canz):
    #Estrazione del gruppo della canzone
    grup = gruppo.objects.filter(canzone__titolo=canz.titolo)
    #Estrazione top ten utente
    topuser = Topten.objects.filter(user=user).order_by('posizione')
    #Estrazione top ten gruppo
    topgruppo = influence.objects.filter(gruppo=grup).order_by('posizione')
    #Calcola Punteggio
    n = int(11)
    punteggio = 0
    for i in topuser:
        for j in topgruppo:
            if i.artist == j.artist:
                a = int(n - i.posizione)
                b = int(n - j.posizione)
                punteggio = int(punteggio + a*b)
    indice = punteggio / 385
    return (indice)