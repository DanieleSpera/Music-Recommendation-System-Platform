import random
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib import auth
from django.contrib.auth import authenticate

from ftft.accountsys.forms import LoginForm

from django.contrib.auth.models import User
from ftft.accountsys.models import Rate, Topten
from ftft.gruppi.models import gruppo,influence
from ftft.canzoni.models import canzone
from ftft.testing.models import Algoritmo,Compilation

from ftft.search.views import fromusertotopten,searchByTopOnBands,searchByTopOnUser,selectfromtopten,searchByRate,frombandtosong,pearsonfromuser,onbandfromuser

def TestHome(request):
    if request.user.is_authenticated():
        #MostraGruppi
        context = {}
        gruppi= gruppo.objects.all().order_by('?')
        context.update({'gruppi' : gruppi})
        return render_to_response('testing/testgruppi.html', context, context_instance=RequestContext(request))
    else:
        #Login
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return HttpResponseRedirect('/testcompilation')
                else:
                    return render_to_response('testing/testhome.html', {'form': form}, context_instance=RequestContext(request))
            else:
                return render_to_response('testing/testhome.html', {'form': form}, context_instance=RequestContext(request))
        else:
            ''' user is not submitting the form, show the login form '''
            form = LoginForm()
            context = {'form': form}
            return render_to_response('testing/testhome.html', context, context_instance=RequestContext(request))

def ShowGrup(request,grup):
    info = gruppo.objects.get(id=grup)
    canzoni = canzone.objects.filter(gruppo=grup)
    context = {'info':info,'canzoni':canzoni}
    if Rate.objects.filter(user=request.user).filter(gruppo=grup):
            for rate in Rate.objects.filter(user=request.user).filter(gruppo=grup):
                context.update({'rate':rate.valutazione})
    return render_to_response('testing/testshowg.html',context,context_instance=RequestContext(request))

def TopTen(request):
    context = {}
    gruppi = gruppo.objects.all()

    #Influenze - TopTen -User
    topten = Topten.objects.filter(user=request.user)
    topinfl = topten.values_list('artist', flat=True)
    topnum = topten.values_list('posizione', flat=True)
    topcomp=[]
    #Componi Top ten
    for i in range(1,11):
        if i in topnum:
            topcomp.append(topten.get(posizione=i))
        else:
            topcomp.append("vuoto")

    #Seleziona influenze direttamente collegate ai gruppi
    influenze = influence.objects.exclude(artist__in=topinfl).filter(gruppo__in=gruppi)
    controller = []
    influnique = []
    for i in influenze:
        if i.artist.nome not in controller:
            controller.append(i.artist.nome)
            influnique.append(i)

    #Lista per ordinare i risultati per lettera
    letters = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    context.update({'gruppi':gruppi,'topten':topcomp,'influenze':influnique,'lettere':letters})
    return render_to_response('testing/testopten.html',context,context_instance=RequestContext(request))

def TesterController(request):
    context = {}
    utenti = User.objects.all()
    gruppi = gruppo.objects.all()

    #Lista Multidimensionale
    riepilogo = []
    for utente in utenti:
        info = []
        info.append(utente)

        #Estrai Gruppi gia votati
        votedgr = Rate.objects.filter(user=utente)
        voted = []
        for vote in votedgr:
            voted.append(vote.gruppo)

        #Estrai top ten
        topten = fromusertotopten(utente.id)
        info.append(topten)
        infl = []
        for pos in topten:
            infl.append(pos.artist.id)

        #Alg Top On Bands
        toponbands=searchByTopOnBands(infl)
        ristobset = [(v, k) for k, v in toponbands.items()]
        ristob = [x for x in ristobset if x[1] not in voted] #Rimuove i gruppi votati
        ristob = sorted(ristob,key=lambda x: x[0], reverse=True)[:15]
        info.append(ristob)

        #Alg Top On User
        toponuser = searchByTopOnUser(infl,usr=utente)
        ristouset = [(v, k) for k, v in toponuser.items()]
        ristou = [x for x in ristouset if x[1] not in voted] #Rimuove i gruppi votati
        ristou = sorted(ristou,key=lambda x: x[0], reverse=True)[:15]
        info.append(ristou)

        #Alg mix
        toponmix = selectfromtopten(infl,usr=utente)
        ristomset = [(v, k) for k, v in toponmix.items()]
        ristom = [x for x in ristomset if x[1] not in voted] #Rimuove i gruppi votati
        ristom = sorted(ristom,key=lambda x: x[0], reverse=True)[:10]
        info.append(ristom)

        #Alg Rate
        toponrate = searchByRate(utente.id)
        ristorset = [(v, k) for k, v in toponrate.items()]
        ristor = [x for x in ristorset if x[1] not in voted] #Rimuove i gruppi votati
        ristor = sorted(ristor,key=lambda x: x[0], reverse=True)[:10]
        info.append(ristor)

        #Componi compilation gruppi dei vari algoritmi
        compilation = []

        for song in ristob[:5]:
            compilation.append(song[1].nome)
        for song in ristou[:5]:
            if song[1].nome not in compilation:
                compilation.append(song[1].nome)
        for song in ristom[:5]:
            if song[1].nome not in compilation:
                compilation.append(song[1].nome)
        for song in ristor[:5]:
            if song[1].nome not in compilation:
                compilation.append(song[1].nome)

        info.append(compilation)

        #Aggiungi gruppi random
        gruppir = gruppo.objects.all().exclude(nome__in=ristobset).exclude(nome__in=ristouset).exclude(nome__in=ristomset).exclude(nome__in=ristorset).exclude(nome__in=voted).order_by('?')[:7]
        contatore = 0
        for song in gruppir:
            if song.nome not in compilation and contatore < 5:
                compilation.append(song.nome)
                contatore += 1

        #Canzoni inserite in compilation
        playlist = []
        comp = Compilation.objects.filter(user=utente.id)
        for c in comp:
            playlist.append(c)
        info.append(playlist)

        riepilogo.append(info)

    # Variabili UTENTI -
    context.update({'riepilogo':riepilogo,'utenti':utenti,'gruppi':gruppi})

    return render_to_response('testing/testercontroller.html',context)

def CompilationController(request):
    context = {}
    utenti = User.objects.all()
    gruppi = gruppo.objects.all()
    voti = Compilation.objects.all()
    # Variabili UTENTI
    riepilogo=[]
    for ut in utenti:
        info = []
        info.append(ut)
        onbands = voti.filter(user = ut, algoritmo=1)
        info.append(onbands)
        onuser = voti.filter(user = ut, algoritmo=2)
        info.append(onuser)
        onmix = voti.filter(user = ut, algoritmo=3)
        info.append(onmix)
        onrate = voti.filter(user = ut, algoritmo=4)
        info.append(onrate)
        oncasual = voti.filter(user = ut, algoritmo=5)
        info.append(oncasual)
        riepilogo.append(info)

    # Tabelle ripetizione
    ripetizione = []
    for i in range(1,6):
        result=[]
        ripset = Compilation.objects.all()
        for grup in gruppi:
            rip = ripset.filter(canzone__gruppo=grup, algoritmo=i).count()
            result.append((grup,rip))
            #Ordina Array
            result.sort(key=lambda tup: tup[1],reverse=True)
        ripetizione.append(result)

    # Gruppi - Voti (media)
    grvot = []
    for grup in gruppi:
        grvotv = voti.filter(canzone__gruppo=grup)
        mediagv = 0
        for v in grvotv:
            if mediagv == 0:
                mediagv = v.voto
            elif v.voto!=0:
                mediagv = (mediagv+v.voto)/2
        grvot.append((grup,round(mediagv,2)))
    grvot.sort(key=lambda tup: tup[1],reverse=True)
    ripetizione.append(grvot)

    #Tabelle Rate
    result2=[]; result3=[]; result4=[]; result5=[]

    rateset = Rate.objects.all()
    for grup in gruppi:
        rates = rateset.filter(gruppo=grup)
        rip = rates.count()
        result2.append((grup,rip))

        # Calcola somma voti
        count = 0
        for r in rates:
            count = count + r.valutazione
        result5.append((grup,count))

        # Calcola somma voti > 3
        rip3 = rates.filter(valutazione__gt=3)
        count = 0
        for r in rip3:
            count = count + r.valutazione
        result4.append((grup,count))

        # Conteggio > 3
        rip2 =  rip3.count()
        result3.append((grup,rip2))

    liste = [result2,result3,result4,result5]
    for x in liste:
        x.sort(key=lambda tup: tup[1],reverse=True)

    ripetizione.extend(liste)


    context.update({'utenti':utenti,'gruppi':gruppi,'riepilogo':riepilogo, 'ripetizione':ripetizione})
    return render_to_response('testing/compilationcontroller.html',context)

def TestCompilation(request):
    if request.user.is_authenticated():
        context={}
        gruppi = gruppo.objects.all()
        playlist = Compilation.objects.filter(user=request.user).order_by('?')
        context.update({'playlist':playlist,'gruppi':gruppi})
        return render_to_response('testing/testcompilation.html',context,context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/testing')

def VoteSong (request):
    if request.method =='POST':
        campo = request.POST['campo']
        vot = request.POST['voto']
        row = Compilation.objects.get(id=campo)
        row.voto=vot
        row.save()
    return HttpResponse ('OK')

def NomiGruppi(request):
    gruppi = influence.objects.all()
    nomi = []
    for g in gruppi:
        if g.artist.nome not in nomi:
            nomi.append(g.artist.nome)
            nomi.append("<br/>")
    return HttpResponse (nomi)


def insertcompilation (request):
    utenti = User.objects.all()

    for utente in utenti:
        #Estrai Gruppi votati
        voted = []
        votedgr = Rate.objects.filter(user=utente)
        for vote in votedgr:
            voted.append(vote.gruppo)

        #Estrai top ten
        infl = []
        topten = fromusertotopten(utente.id)
        for pos in topten:
            infl.append(pos.artist.id)

        #Alg -----------------------------------------------------------------------
        #Alg Top On Bands - Togli gruppi votati - ordina
        gruppisel=[]
        funzioni = [searchByTopOnBands,searchByTopOnUser,selectfromtopten,searchByRate]
        for funzione in funzioni:
            if funzioni.index(funzione)==3:
                toponbands=funzione(utente.id)
            elif funzioni.index(funzione)==1 or funzioni.index(funzione)==2:
                toponbands=funzione(infl,usr=utente)
            else:
                toponbands=funzione(infl)

            ristobset = [(v, k) for k, v in toponbands.items()]
            for g in ristobset:
                if g[1].nome not in gruppisel:
                    gruppisel.append(g[1].nome)
            ristob = [x for x in ristobset if x[1] not in voted] #Rimuove i gruppi votati
            ristob = sorted(ristob,key=lambda x: x[0], reverse=True)[:5]
            #componi lista gruppi
            listagruppi =[]
            for r in ristob:
                listagruppi.append(r[1])
            #Estrai Canzoni
            canzoni=frombandtosong(listagruppi)
            #Inserisci in database
            alg = Algoritmo.objects.get(id=(funzioni.index(funzione)+1))
            for s in canzoni:
                checktupla=Compilation.objects.filter(user=utente,canzone=s)
                if len(checktupla) > 0:
                    for tupla in checktupla:
                        tupla.algoritmo.add(alg)
                else:
                    compbands = Compilation(user=utente,canzone=s, voto=0)
                    compbands.save()
                    compbands.algoritmo.add(alg)

        #Aggiungi gruppi random
        gruppir = gruppo.objects.all().exclude(nome__in=gruppisel).exclude(nome__in=voted).order_by('?')[:7]
        canzonirandom=frombandtosong(gruppir)
        contatore = 0
        for canz in canzonirandom:
            if len(Compilation.objects.filter(user=utente,canzone=canz))>0:
                pass
            elif contatore < 5:
                compbands = Compilation(user=utente,canzone=canz, voto=0)
                compbands.save()
                compbands.algoritmo.add(5)
                contatore += 1

    return HttpResponse ("Inserito tutto!")

def column(matrix, i):
    return [row[i] for row in matrix]

def risultati2 (request):
    prova= []
    utenti = User.objects.filter(username__in=['sabatino','erica'])
    #utenti = User.objects.all()

    tob = []
    tou = []
    mix = []
    per = []
    cas = []

    for utente in utenti:
        #Estrai top ten
        topten = fromusertotopten(utente.id)
        infl = []
        for pos in topten:
            infl.append(pos.artist.id)

        #Alg Top On Bands-------------------------------------------------------
        toponbands = searchByTopOnBands(infl)
        toponbands = toponbands.items()
        #Estrai votazioni effettuate su canzoni e gruppi consigliati
        votiuser = Compilation.objects.filter(user=utente,algoritmo=1).exclude(voto=0)
        voti = []
        for key,value in toponbands:
            voti.append([utente,key,"%.2f" %(value/385*10)])

        #Estrai e relativi gruppi
        canzoniuser=votiuser.values_list('canzone', flat=True)
        gruppiuser=gruppo.objects.filter(canzone__in=canzoniuser)
        for rec in voti:
            if rec[1] in gruppiuser:
                voto = votiuser.filter(canzone__gruppo=rec[1])
                buffera = rec
                for v in voto:
                    buffera.append(v.voto)
                tob.append(rec)

        #Alg Top On User--------------------------------------------------------
        toponusers = searchByTopOnUser(infl)
        toponusers = toponusers.items()
        #Estrai votazioni effettuate su canzoni e gruppi consigliati
        votiuser = Compilation.objects.filter(user=utente,algoritmo=2).exclude(voto=0)
        voti = []
        for key,value in toponusers:
            voti.append([utente,key,"%.2f" %(value/385*10)])

        #Estrai e relativi gruppi
        canzoniuser=votiuser.values_list('canzone', flat=True)
        gruppiuser=gruppo.objects.filter(canzone__in=canzoniuser)
        for rec in voti:
            if rec[1] in gruppiuser:
                voto = votiuser.filter(canzone__gruppo=rec[1])
                buffera = rec
                for v in voto:
                    buffera.append(v.voto)
                tou.append(rec)
        #Alg Top On Mix--------------------------------------------------------
        toponmix = selectfromtopten(infl)
        toponmix = toponmix.items()
        #Estrai votazioni effettuate su canzoni e gruppi consigliati
        votiuser = Compilation.objects.filter(user=utente,algoritmo=3).exclude(voto=0)
        voti = []
        for key,value in toponmix:
            voti.append([utente,key,"%.2f" %(value/385*10)])

        #Estrai e relativi gruppi
        canzoniuser=votiuser.values_list('canzone', flat=True)
        gruppiuser=gruppo.objects.filter(canzone__in=canzoniuser)
        for rec in voti:
            if rec[1] in gruppiuser:
                voto = votiuser.filter(canzone__gruppo=rec[1])
                buffera = rec
                for v in voto:
                    buffera.append(v.voto)
                mix.append(rec)
        #Alg Top On Rate--------------------------------------------------------
        toponrate = searchByRate(utente.id)
        toponrate = toponrate.items()
        #Estrai votazioni effettuate su canzoni e gruppi consigliati
        votiuser = Compilation.objects.filter(user=utente,algoritmo=4).exclude(voto=0)
        voti = []
        for key,value in toponrate:
            voti.append([utente,key,"%.2f" %(value/10)])

        #Estrai e relativi gruppi
        canzoniuser=votiuser.values_list('canzone', flat=True)
        gruppiuser=gruppo.objects.filter(canzone__in=canzoniuser)
        for rec in voti:
            if rec[1] in gruppiuser:
                voto = votiuser.filter(canzone__gruppo=rec[1])
                buffera = rec
                for v in voto:
                    buffera.append(v.voto)
                per.append(rec)
        #Alg Top On Casuale-----------------------------------------------------
        #Estrai votazioni effettuate su canzoni e gruppi consigliati
        votiuser = Compilation.objects.filter(user=utente,algoritmo=5).exclude(voto=0)
        voti = []
        for rec in votiuser:
            cas.append([rec.user,rec.canzone,random.randint(1,10),rec.voto])
    #Preparazione a risultati
    risset= [['Top on Band',tob],['Top on User',tou],['Top on mix',mix],['Pearson',per],['Casual',cas]]
    mae = []
    devst = []
    for alg in risset:
        #MAE
        n=len(alg[1])
        sommdiff = float(0)
        for ris in alg[1]:
            diff= float(ris[2])-float(ris[3])
            sommdiff = sommdiff + diff
        maealg = sommdiff/n
        mae.append(maealg)

        #Deviazione standard
        sommdiff = float(0)
        for ris in alg[1]:
            diff= ((float(ris[2])-float(ris[3]))-float(maealg))**2
            sommdiff = sommdiff + diff
        ds = (sommdiff/n)**0.5
        devst.append(ds)
        prova.append(ds)

    ut1= User.objects.get(username="Sabatino")
    ut2= User.objects.get(username="Erica")
    vari=pearsonfromuser(ut1.id,ut2.id)
    prova.append(vari)

    context = {'prova':prova,'utenti':utenti,'onband':toponbands,'voti':voti,'alg1':tob,'alg2':tou,'alg3':mix,'alg4':per,'alg5':cas}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))
    #return HttpResponse (toponbands)

#Risultati----------------------------------------------------------------------
def risultatipearson(request):
    #Variabili visualizzazione
    prova = []
    utenti = []
    voti = []
    indicipearson = []
    predizioni = []
    differenzE = []
    test = []

    #PARTE 1
    #ESTRAZIONE UTENTI
    allrecords=Compilation.objects.all().exclude(voto=0)
    medieutenti = []
    user = []
    # Estrai tutti utenti da prendere in consierazione
    for r in allrecords:
        if r.voto != 0:
            if r.user not in user:
                user.append(r.user)
    #PRECALCOLO MEDIE
    for u in user:
        #estrai tutte valutazioni effettuate dall'utente
        votiut = allrecords.values_list('voto', flat=True).filter(user=u)
        medieutenti.append([u,float(sum(votiut)/len(votiut))])
    #PRECALCOLO PEARSON
    buffer = []
    for utentea in user:
        for utenteb in user:
            if utentea != utenteb:
                if utenteb not in buffer:
                    inpea = pearsonfromuser(utentea.id,utenteb.id)
                    indicipearson.append([utentea.id,utenteb.id,inpea])
        buffer.append(utentea)

    #PARTE 2
    #Lista risultato differenze
    for utente in user:
        #Media voti utente considerato Estrai da lista
        for med in medieutenti:
            if med[0] == utente:
                mediavotiuta = med[1]
                break

        #estrai valutazioni effettuate
        canzonivalutate = allrecords.filter(user=utente)
        canzonidapredire = canzonivalutate.values_list('canzone', flat=True)
        recordcomuni = allrecords.filter(canzone__in=canzonidapredire).exclude(user=utente)

        #Per ogni canzone calcola predizione e inserisci in array
        for canz in canzonidapredire:
            utcons=recordcomuni.filter(canzone=canz)
            sommnum = 0
            sommpears = 0
            #Per ogni utente con canzoni in comune - Calcola indice e prepara sommatorie
            for u in utcons:
                #Calcola indice e prepara sommatoria del denominatore
                for i in indicipearson:
                    if i[0] == utente.id or i[1] == utente.id:
                        if i[0] == u.user.id or i[1] == u.user.id:
                            pearson = i[2]
                            break
                if pearson > 0.0 :
                    #prendi media da lista medie
                    for med in medieutenti:
                        if med[0] == u.user:
                            media = med[1]
                            break
                    #Calcola numeratore e somma alla sommatoria
                    sommpears = sommpears + pearson
                    numeratore = pearson * (u.voto - media)
                    sommnum = sommnum + numeratore
            #Calcola predizione
            if sommpears > 0:
                #test.append(pearson)
                predizione = float(mediavotiuta) + (float(sommnum)/float(sommpears))
                originalvoto = canzonivalutate.get(canzone=canz)
                predizioni.append([utente,originalvoto.voto,predizione,abs(predizione-originalvoto.voto)])

    '''for i in predizioni:
        test.append(i[3])'''
    mae = sum(x[3] for x in predizioni)/len(predizioni)
    sde = (sum(abs(x[3]-mae)**2 for x in predizioni)/len(predizioni))**0.5

    prova = [mae,sde]

    #test
    '''lunghezza = len(predizioni)
    buffer = []
    test2 = []
    for i in test:
        i = round(5*i)/5
        i = "%.1f" % i
        if i not in buffer:
            test2.append([i,0])
            buffer.append(i)
        else:
            indice = buffer.index(i)
            test2[indice][1] = test2[indice][1]+1
    test = test2
    test.sort(key=lambda x: x[0])
    #test.sort()
    test.append(lunghezza)'''
    context = {'prova':prova,'onband':test,'voti':voti,'predizioni':predizioni,'differenze':differenzE}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))

def risultationband(request):
    prova = "" #del
    allrectopred = Compilation.objects.exclude(voto=0)
    listautenti = []
    listacanzoni = []
    toptenutenti = []
    toptengruppi = []
    predizioni = []
    test = []
    #Estrai tutti utenti presenti
    for rec in allrectopred:
        if rec.user not in listautenti:
            listautenti.append(rec.user)
    #Estrai tutte canzoni presenti
        if rec.canzone not in listautenti:
            listacanzoni.append(rec.canzone)

    #Precalcolo
    for ut in listautenti:
        votiut = allrectopred.values_list('voto', flat=True).filter(user=ut)
        #Media voti effettuati
        media = float(sum(votiut)/len(votiut))
        #Top ten utente
        topuser = Topten.objects.filter(user=ut).order_by('posizione')
        #Componi toptenutenti utente,topten,voto medio,voto minimo
        toptenutenti.append([ut,topuser,media,min(votiut)])
    for canz in listacanzoni:
        voticanz = allrectopred.values_list('voto', flat=True).filter(canzone=canz)
        # Media voti ricevuti
        media = float(sum(voticanz)/len(voticanz))
        #Estrazione del gruppo della canzone
        grup = gruppo.objects.filter(canzone__titolo=canz.titolo)
        #Top ten gruppo
        topgruppo = influence.objects.filter(gruppo=grup).order_by('posizione')
        #Componi toptenutenti utente,topten,voto medio
        toptengruppi.append([canz,topgruppo,media,min(voticanz)])
    for rec in allrectopred:
    #Calcola Punteggio
        n = int(11)
        punteggio = 0
        #Recupera top ten media e voto minimo utente
        for ut in toptenutenti:
            if ut[0] == rec.user:
                topuser = ut[1]
                mediautente = ut[2]
                votomin = ut[3]
        #Recupera top ten media e voto canzone
        for cn in toptengruppi:
            if cn[0] == rec.canzone:
                topgruppo = cn[1]
                mediacanzone = cn[2]
                votominc = cn[3]

        #Calcola l'indice
        for i in topuser:
            for j in topgruppo:
                if i.artist == j.artist:
                    a = int(n - i.posizione)
                    b = int(n - j.posizione)
                    punteggio = int(punteggio + a*b)
        indice = punteggio / 385

        #Calcolca predizione voto 2 offset
        predizione = (indice*((mediautente+mediacanzone)/2))+((votomin+votominc)/2)+2.5
        #Aggiungi a predizioni
        predizioni.append([rec.user,rec.voto,predizione,abs(predizione-rec.voto),rec.canzone])
        #test.append(indice)

    #Calcolo errori
    mae = sum(x[3] for x in predizioni)/len(predizioni)
    sde = (sum(abs(x[3]-mae)**2 for x in predizioni)/len(predizioni))**0.5
    prova = [mae,sde]

    '''#test
    lunghezza = len(predizioni)
    buffer = []
    test2 = []
    for i in test:
        i = round(20*i)/20
        i = "%.2f" % i
        if i not in buffer:
            test2.append([i,1])
            buffer.append(i)
        else:
            indice = buffer.index(i)
            test2[indice][1] = test2[indice][1]+1
    test = test2
    test.sort(key=lambda x: x[0])
    test.append(lunghezza)'''

    context = {'prova':prova,'onband':test}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))

def risultationuser(request):
    prova=0
    listautenti = []
    listaindici = []
    toptenutenti = []
    predizioni = []
    test = []
    allrectopred = Compilation.objects.exclude(voto=0)

    #Estrai tutti utenti presenti
    for rec in allrectopred:
        if rec.user not in listautenti:
            listautenti.append(rec.user)

    #Precalcolo
    for ut in listautenti:
        votiut = allrectopred.values_list('voto', flat=True).filter(user=ut)
        #Media voti effettuati
        media = float(sum(votiut)/len(votiut))
        #Top ten utente
        topuser = Topten.objects.filter(user=ut).order_by('posizione')
        #Componi toptenutenti utente,topten,voto medio,voto minimo
        toptenutenti.append([ut,topuser,media,min(votiut)])

    #Calcola pesi tra utenti
    buffer = []
    for ut1 in toptenutenti:
        for ut2 in toptenutenti:
            if ut2 != ut1:
                if ut2 not in buffer:
                    #Calcola indice
                    n = int(11)
                    punteggio = 0
                    #Calcola l'indice ut = top ten utenti
                    for i in ut1[1]:
                        for j in ut2[1]:
                            if i.artist == j.artist:
                                a = int(n - i.posizione)
                                b = int(n - j.posizione)
                                punteggio = int(punteggio + a*b)
                    indice = punteggio / 385
                    listaindici.append([ut1[0],ut2[0],indice])
        buffer.append(ut1)

    for vot1 in allrectopred:
        #Recupera media utente
        for m in toptenutenti:
            if m[0] == vot1.user:
                media1 = m[2]
                break
        #Inizializza sommatorie
        sommnum = 0
        sommpred = 0
        #trova gli altri record che riguardano lo stesso gruppo
        rectest = allrectopred.filter(canzone=vot1.canzone).exclude(user=vot1.user)
        #calcola sommatorie
        for vot2 in rectest:
            #Recupera media utente
            for m in toptenutenti:
                if m[0] == vot2.user:
                    media2 = m[2]
                    break

            voto = vot2.voto
            #Recupera peso confronto top ten
            for indice in listaindici:
                if vot1.user == indice[0] or vot1.user == indice[1]:
                    if vot2.user == indice[0] or vot2.user == indice[1]:
                        index = indice[2]
                        break

            if index > 0.0:
                #Aggiorna somma predizioni (denominatore)
                sommpred = sommpred + index
                numeratore = (voto-media2)*index
                sommnum = sommnum + numeratore
        #Calcola predizione voto
        if sommpred !=0:
            predizione = media1 + (sommnum/sommpred) + 0.014


        # Aggiungi a lista predizioni
        predizioni.append([vot1.user,vot1.voto,predizione,abs(predizione-vot1.voto)])
        test.append(index)

    #Calcolo errori
    mae = sum(x[3] for x in predizioni)/len(predizioni)
    sde = (sum(abs(x[3]-mae)**2 for x in predizioni)/len(predizioni))**0.5
    #prova = [mae,sde,len(predizioni)]


    #test
    lunghezza = len(predizioni)
    buffer = []
    test2 = []
    for i in test:
        i = round(20*i)/20
        i = "%.2f" % i
        if i not in buffer:
            test2.append([i,1])
            buffer.append(i)
        else:
            indice = buffer.index(i)
            test2[indice][1] = test2[indice][1]+1
    test = test2
    test.sort(key=lambda x: x[0])
    test.append(lunghezza)
    context = {'prova':prova,'onband':test}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))

'''def risultationuser(request):
    allrectopred = Compilation.objects.exclude(voto=0)
    test=[]
    listautenti=[]
    #Estrai tutti utenti presenti
    for rec in allrectopred:
        if rec.user not in listautenti:
            listautenti.append(rec.user)
    risultati = []
    for ut in listautenti:
        totale = []
        for rec in allrectopred:
            if rec.user == ut:
                totale.append(rec.voto)
        risultati.append(sum(x for x in totale)/len(totale))
    context = {'prova':allrectopred,'onband':risultati}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))'''



def risultationmix(request):
    prova=0
    listautenti = []
    listacanzoni = []
    listaindici = []
    toptenutenti = []
    toptengruppi = []
    predizionimix = []
    predizionimix2 = []
    predizionipearson = []
    predizioniuser = []
    predizioniband = []
    indicepearson = []
    indicegruppi = []
    test = []
    nonvalutate = 0
    allrectopred = Compilation.objects.exclude(voto=0)

    #Estrai tutti utenti presenti
    for rec in allrectopred:
        if rec.user not in listautenti:
            listautenti.append(rec.user)
    #Estrai tutte canzoni presenti
        if rec.canzone not in listautenti:
            listacanzoni.append(rec.canzone)

    #Precalcolo
    for ut in listautenti:
        votiut = allrectopred.values_list('voto', flat=True).filter(user=ut)
        #Media voti effettuati
        media = float(sum(votiut)/len(votiut))
        #Top ten utente
        topuser = Topten.objects.filter(user=ut).order_by('posizione')
        #Componi toptenutenti utente,topten,voto medio,voto minimo
        toptenutenti.append([ut,topuser,media,min(votiut)])

    for canz in listacanzoni:
        voticanz = allrectopred.values_list('voto', flat=True).filter(canzone=canz)
        # Media voti ricevuti
        media = float(sum(voticanz)/len(voticanz))
        #Estrazione del gruppo della canzone
        grup = gruppo.objects.filter(canzone__titolo=canz.titolo)
        #Top ten gruppo
        topgruppo = influence.objects.filter(gruppo=grup).order_by('posizione')
        #Componi toptenutenti utente,topten,voto medio
        toptengruppi.append([canz,topgruppo,media,min(voticanz)])

    #Calcola INDICI by Band
    for rec in allrectopred:
    #Calcola Punteggio
        n = int(11)
        punteggio = 0
        #Recupera top ten media e voto minimo utente
        for ut in toptenutenti:
            if ut[0] == rec.user:
                topuser = ut[1]
                mediautente = ut[2]
                votomin = ut[3]
        #Recupera top ten media e voto canzone
        for cn in toptengruppi:
            if cn[0] == rec.canzone:
                topgruppo = cn[1]
                mediacanzone = cn[2]
                votominc = cn[3]

        #Calcola l'indice
        for i in topuser:
            for j in topgruppo:
                if i.artist == j.artist:
                    a = int(n - i.posizione)
                    b = int(n - j.posizione)
                    punteggio = int(punteggio + a*b)
        indice = punteggio / 385
        indicegruppi.append([rec.id,indice])

        #Calcolca predizione voto 2 offset
        predizioneband = (indice*((mediautente+mediacanzone)/2))+((votomin+votominc)/2)+2
        #Aggiungi a predizioni
        predizioniband.append([rec.user,rec.voto,predizioneband,abs(predizioneband-rec.voto),rec.canzone])
    #FINE Indice by Band

    #Calcola pesi tra utenti
    buffer = []
    for ut1 in toptenutenti:
        for ut2 in toptenutenti:
            if ut2 != ut1:
                if ut2 not in buffer:
                    #Calcola indice
                    n = int(11)
                    punteggio = 0
                    #Calcola l'indice ut = top ten utenti
                    for i in ut1[1]:
                        for j in ut2[1]:
                            if i.artist == j.artist:
                                a = int(n - i.posizione)
                                b = int(n - j.posizione)
                                punteggio = int(punteggio + a*b)
                    indice = punteggio / 385
                    listaindici.append([ut1[0],ut2[0],indice])
                    #calcola pearson
                    inpea = pearsonfromuser(ut1[0].id,ut2[0].id)
                    indicepearson.append([ut1[0],ut2[0],inpea])
        buffer.append(ut1)

    for vot1 in allrectopred:
        #Recupera media utente
        for m in toptenutenti:
            if m[0] == vot1.user:
                media1 = m[2]
                break
        #Inizializza sommatorie

        #Pearson
        sommnumpea = 0
        sommpredpea = 0
        #OnUser
        sommnumusr = 0
        sommpredusr = 0
        #Mix
        sommnum = 0
        sommpred = 0
        #Mix2
        for x in indicegruppi:
            if x[0] == vot1.id:
                indicegruppo = x[1]
                break
        sommnummix2 = 0
        sommpredmix2 = 0


        #trova gli altri record che riguardano lo stesso gruppo (escludendo canzone considerata)
        rectest = allrectopred.filter(canzone=vot1.canzone).exclude(user=vot1.user)
        #calcola sommatorie
        for vot2 in rectest:
            #Recupera media utente
            for m in toptenutenti:
                if m[0] == vot2.user:
                    media2 = m[2]
                    break

            voto = vot2.voto
            #Recupera peso confronto top ten
            for indice in listaindici:
                if vot1.user == indice[0] or vot1.user == indice[1]:
                    if vot2.user == indice[0] or vot2.user == indice[1]:
                        index = indice[2]
                        break

            #Recupera indice Pearson
            for indice in indicepearson:
                if indice[0] == vot1.user or indice[1] == vot1.user:
                    if indice[0] == vot2.user or indice[1] == vot2.user:
                        indexpea = indice[2]
                        break


            #PREDIZIONE PEARSON
            #Aggiorna somma predizioni (denominatore)
            if indexpea > 0.0:
                sommpredpea = sommpredpea + indexpea
                numeratorepea = indexpea * (voto-media2)
                sommnumpea = sommnumpea + numeratorepea

            #PREDIZIONE BY USER
            #Aggiorna somma predizioni (denominatore)
            if index > 0.0:
                sommpredusr = sommpredusr + index
                numeratoreusr = index * (voto-media2)
                sommnumusr = sommnumusr + numeratoreusr

            #PREDIZIONE BY PEA-USER
            #Aggiorna somma predizioni (denominatore)
            if index or indexpea > 0.0:
                sommpred = sommpred + ((index + indexpea)/2)
                numeratore = index * (voto-media2)
                sommnum = sommnum + numeratore

            #PREDIZIONE BY PEA-USER-GROUP
            #Aggiorna somma predizioni (denominatore)
            if index or indexpea or indicegruppo > 0.0:
                sommpredmix2 = sommpredmix2 + ((index + indexpea + indicegruppo)/3)
                numeratoremix2 = indicegruppo * (voto-media1)
                sommnummix2 = sommnummix2 + numeratoremix2

        #Calcola predizioni voto
        '''if sommpred !=0:
            predizione = float(media1) + (float(sommnum)/float(sommpred)) + 0.014'''
        if sommpredpea !=0:
            predizionepea = float(media1) + (float(sommnumpea)/float(sommpredpea))
        if sommpredusr !=0:
            predizioneusr = float(media1) + (float(sommnumusr)/float(sommpredusr)) + 0.014
        if sommpred !=0:
            predizionemix = float(media1) + (float(sommnum)/float(sommpred)) + 0.014
        if sommpredmix2 !=0:
            predizionemix2 = float(media1) + (float(sommnummix2)/float(sommpredmix2))

        # Aggiungi a lista predizioni
        predizionimix.append([vot1.user,vot1.voto,predizionemix,abs(predizionemix-vot1.voto)])
        predizionipearson.append([vot1.user,vot1.voto,predizionepea,abs(predizionepea-vot1.voto),vot1.canzone.titolo])
        predizioniuser.append([vot1.user,vot1.voto,predizioneusr,abs(predizioneusr-vot1.voto)])
        predizionimix2.append([vot1.user,vot1.voto,predizionemix2,abs(predizionemix2-vot1.voto)])
        #test.append(((index + indexpea)/2))

    #Calcolo errori
    maemix = sum(x[3] for x in predizionimix)/len(predizionimix)
    sdemix = (sum(abs(x[3]-maemix)**2 for x in predizionimix)/len(predizionimix))**0.5
    #Calcolo pea
    maepae = sum(x[3] for x in predizionipearson)/len(predizionipearson)
    sdepae = (sum(abs(x[3]-maepae)**2 for x in predizionipearson)/len(predizionipearson))**0.5
    #Calcolo ByUser
    maeusr = sum(x[3] for x in predizioniuser)/len(predizioniuser)
    sdeusr = (sum(abs(x[3]-maeusr)**2 for x in predizioniuser)/len(predizioniuser))**0.5
    #Calcolo ByGruppo
    maeband = sum(x[3] for x in predizioniband)/len(predizioniband)
    sdeband = (sum(abs(x[3]-maeband)**2 for x in predizioniband)/len(predizioniband))**0.5
    #Calcolo ByGruppo
    maemix2 = sum(x[3] for x in predizionimix2)/len(predizionimix2)
    sdemix2 = (sum(abs(x[3]-maemix2)**2 for x in predizionimix2)/len(predizionimix2))**0.5

    rismix = ["Mix",maemix,sdemix,nonvalutate]
    rispae = ["Pearson",maepae,sdepae,nonvalutate]
    risusr = ["ByUser",maeusr,sdeusr,nonvalutate]
    risband = ["ByBand",maeband,sdeband,nonvalutate]
    rismix2 = ["Mix2",maemix2,sdemix2,nonvalutate]

    risultati = [rismix,rispae,risusr,risband,rismix2]
    #prova = [maeusr,sdeusr,len(predizioniuser)]

    '''#test
    lunghezza = len(predizionimix)
    buffer = []
    test2 = []
    for i in test:
        i = round(15*i)/15
        i = "%.1f" % i
        if i not in buffer:
            test2.append([i,1])
            buffer.append(i)
        else:
            indice = buffer.index(i)
            test2[indice][1] = test2[indice][1]+1
    test = test2
    test.sort(key=lambda x: x[0])
    test.append(lunghezza)'''

    context = {'prova':prova,'onband':risultati,'voti':test}
    return render_to_response('testing/risultati.html',context,context_instance=RequestContext(request))