from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'precos'

urlpatterns =[
    path('', views.todosprecos, name='home' ),
    path('<int:id>/', views.verpreco, name='verpreco'),
    path('alterar/',views.alterar_faixa, name='alterar_faixa'),
    path('importar/',views.importar, name='importar'),
    path('subir/',views.enviaromni, name='subir'),
    path('portais/',views.verpreco_portais, name='portais'),
    path('novanota/',views.nova_nota, name='novanota'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)