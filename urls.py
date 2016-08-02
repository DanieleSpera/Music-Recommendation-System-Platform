from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.contrib import admin
from ftft.gruppi.models import gruppo
from ftft.servpage.models import tutorial

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ftft.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    #TEST
    url(r'^hello/$', 'ftft.accountsys.views.hello',name="hello"),

    # HOME
    url(r'^$', 'ftft.accountsys.views.home', name='home'),
    url(r'^2$', 'ftft.accountsys.views.home', name='home'),
    url(r'^$', 'ftft.testing.views.TestHome', name='home'),
    url(r'^profile$', 'ftft.accountsys.views.profile'),

    # ACCOUNT
        # Log
    url(r'^accounts/login/$', 'ftft.accountsys.views.logacc'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

        # Registration:
    url(r'^accounts/register/$', 'ftft.accountsys.views.register_user'),
    url(r'^accounts/cprofile/$', 'ftft.accountsys.views.cprofile'),

        #Setting
    url(r'^setting$', 'ftft.accountsys.views.setting'),

        #Influence
    url(r'^deleteinfluence/$', 'ftft.accountsys.views.deleteinfluence'),
    url(r'^getfartist/$', 'ftft.accountsys.views.getfartist'),
    url(r'^insinchart/$', 'ftft.accountsys.views.insinchart'),
    url(r'^insartist/$', 'ftft.gruppi.views.insartist'),

        # Gestione Play List/Valutazioni:
    url(r'^addplaylist/$', 'ftft.accountsys.views.addplaylist'),
    url(r'^rate/$', 'ftft.accountsys.views.rate'),
    url(r'^playertest/$', 'ftft.accountsys.views.playertest'),

        # Registrazione Ascolti:
    url(r'^recplay/$', 'ftft.accountsys.views.recplay'),

    # GRUPPI:
    url(r'^insgrup/$', 'ftft.gruppi.views.insgrup'),
    url(r'^showgrups/$', ListView.as_view(
        model=gruppo,
        context_object_name = 'gruppi',
        template_name='showg.html'
    )),
    url(r'^modgruppo/(\d+)/$', 'ftft.gruppi.views.modgrup'),
    url(r'^showgrup/(\d+)/$', 'ftft.gruppi.views.showgrup'),


    #CANZONI
    url(r'^delsong/(\d+)/$', 'ftft.gruppi.views.delsong'),
            #Deposito
    url(r'^depsong/$', 'ftft.canzoni.views.depsong'),# Deposito
    url(r'^depconfirm/$', 'ftft.canzoni.views.depconfirm'),# Deposito2

    # SERVPAGE:
    url(r'^faq/$', 'ftft.servpage.views.faq'),# Inserisci canzone in split
        # Tutorial
    url(r'^instutorial/$', 'ftft.servpage.views.instutorial'),
    url(r'^tutorial/$', ListView.as_view(
        model=tutorial,
        context_object_name = 'tutorials',
        template_name='tutorial.html'
    )),
            # SplitAlbum
    url(r'^splitcd/$', 'ftft.servpage.views.splitcd'),# SplitAlbum
    url(r'^splitins/$', 'ftft.servpage.views.splitins'),# Inserisci canzone in split

    #SEARCH
    url(r'^search/$', 'ftft.search.views.search'),
    url(r'^searchbytag/$', 'ftft.search.views.searchByTag'),
    url(r'^searchbyplaylist/$', 'ftft.search.views.searchbyplaylist'),
    url(r'^searchbytopten/$', 'ftft.search.views.searchByTopTen'),
    url(r'^searchbydragdrop/$', 'ftft.search.views.searchByDragDrop'),
    url(r'^searchbyrate/$', 'ftft.search.views.searchByRate'),

    #TESTING
    #url(r'^testing/$', 'ftft.testing.views.TestHome'),
    url(r'^testshowg/(\d+)/$', 'ftft.testing.views.ShowGrup'),
    url(r'^testopten/$', 'ftft.testing.views.TopTen'),
    url(r'^testercontroller/$', 'ftft.testing.views.TesterController'),
    url(r'^compilationcontroller/$', 'ftft.testing.views.CompilationController'),
    url(r'^testcompilation/$', 'ftft.testing.views.TestCompilation'),
    url(r'^votesong/$', 'ftft.testing.views.VoteSong'),
    url(r'^insertcompilation/$', 'ftft.testing.views.insertcompilation'),
    url(r'^nomigruppi/$', 'ftft.testing.views.NomiGruppi'),

    #RISULTATI TEST
    url(r'^risultatipearson/$', 'ftft.testing.views.risultatipearson'),
    url(r'^risultationband/$', 'ftft.testing.views.risultationband'),
    url(r'^risultationuser/$', 'ftft.testing.views.risultationuser'),
    url(r'^risultationmix/$', 'ftft.testing.views.risultationmix'),

    (r'^provahtml/$', TemplateView.as_view(template_name='testing/SM2.html')),
)