from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'catalogo'

urlpatterns =[
    path('', views.notas, name='home'),
    path('moveis/',views.notas, name='moveis'),
    path('correcoes/',views.correcao, name='correcao'),
    path('correcoes/<int:id>/',views.vercorrecao, name='correcaoind'),
    path('post/',views.edit, name='post'),
    path('novacorrecao/',views.novacorrecao, name='novacorrecao'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
