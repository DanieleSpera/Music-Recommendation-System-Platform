import os
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from ftft.gruppi.models import  gruppo, gruppoform, famusartist, influence, famusartistform
from ftft.gruppi.forms import modgrupform
from ftft.canzoni.models import canzone, deposito
from ftft.canzoni.forms import inscanz
from ftft.accountsys.models import Drinkers, Playlist, Rate

#Inserisci gruppo
def insgrup(request):
    c = {}
    c.update(csrf(request))
    form = gruppoform
    if request.method =='POST':
        formset=form(request.POST,request.FILES)
        if formset.is_valid():
            formset.referente = Drinkers.objects.get(user=request.user.id)
            formset.save()
        # ... view code here
        ok ="Gruppo Inserito con successo"
        c.update({'ok':ok })
        return render_to_response('insgrup.html',c)
    form = gruppoform()
    c.update({'form':form })
    return render_to_response('back/insgrup.html',c)

#def showgrups(request):
#    gruppi= gruppo.objects.all()
#    return render_to_response('showg.html',{'gruppi':gruppi,'pt':pt})

# Pagina gruppo
def showgrup(request,grup):
    info = gruppo.objects.get(id=grup)
    canzoni = canzone.objects.filter(gruppo=grup)
    context = {'info':info,'canzoni':canzoni}
    if request.user.is_authenticated():
        playlist = Playlist.objects.values_list('canzone', flat=True).filter(user=request.user)
        context.update({'playlist':playlist })
        if Rate.objects.filter(user=request.user).filter(gruppo=grup):
            for rate in Rate.objects.filter(user=request.user).filter(gruppo=grup):
                context.update({'rate':rate.valutazione})
    return render_to_response('showgn.html',context,context_instance=RequestContext(request))

#Modifica Gruppo
@login_required
def modgrup(request, gruppo_id):
    band=gruppo.objects.get(id=gruppo_id)
    bands = gruppo.objects.filter(referente=request.user.id)
    canzoni = canzone.objects.filter(gruppo=band)
    if band in bands:
        c = {}
        c.update(csrf(request))
        # Utente autenticato
        if request.user.is_authenticated():
            if request.method == 'POST':
                # Modifica GRuppo
                if request.POST['action'] == 'gruppo':
                    formset=modgrupform(request.POST,request.FILES,instance=band)

                    if request.POST.get('biografia') is None:
                        band.biografia = "Nessuna biografia inserita"
                    '''if request.FILES.get('logo'):
                        #os.remove(os.path.join(settings.MEDIA_ROOT+"/logogruppi", band.nome))
                        #band.logo.delete(save=True)
                        band.logo.delete()
                        image_file = request.FILES['logo']
                        band.logo.save(band.nome, image_file)'''

                    if formset.is_valid():
                        band.save()
                    else:
                        return HttpResponse("Form Non Valido")
		        # Inserisci Canzone
                if request.POST['action'] == 'canzone':
                    formset=inscanz(request.POST,request.FILES)
                    if formset.is_valid():
                        prova = formset.save()
                        prova.gruppo.add(band)
                        return HttpResponseRedirect('/modgruppo/'+gruppo_id)
                    else:
                        return HttpResponse(request.POST)
            # Passaggio variabili alla pagina
            c.update({'user' : request.user,'band':band,'canzoni':canzoni})
            # Maschera modifica dati gruppi
            formmod=modgrupform(instance=band)
            c.update({'formmod':formmod})
            # Maschera inserimento canzoni
            c.update({'formcanz':inscanz})
            # Maschera inserimento gruppi famosi
            formart = famusartistform()
            c.update({'formart':formart})
            # Lista Canzoni depositate
            listalic = deposito.objects.values_list('canzone',flat=True)
            songdep = canzone.objects.filter(gruppo=band).filter(id__in=listalic)
            c.update({'depositate':songdep})
            # Estrapolazione influenze
            influ = influence.objects.filter(gruppo=gruppo_id)
            toptenpos = influence.objects.values_list('posizione',flat=True).filter(gruppo=gruppo_id)
            position=[i+1 for i in range(10)]
            c.update({'position':position,'influ':influ,'toptenpos':toptenpos})
            return render_to_response('back/modgrup.html', c, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/profile')


# Elimina canzone
@login_required
def delsong(request,id_song):
    song = canzone.objects.get(id=id_song)
    song.delete()
    song.contenuto.delete(save=False)
    return HttpResponse("Cancellata")

# Inserisci Artista
@login_required
def insartist(request):
    if request.method == 'POST':
        nomeartista = request.POST.get('nome')
        genereartista = request.POST.get('genere')
        if famusartist.objects.filter(nome=nomeartista):
            return HttpResponse("Artista presente")
        else:
            newartist = famusartist(nome=nomeartista,genere=genereartista)
            newartist.save()
            return HttpResponse("Aggiunto")