from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns =[
    path('', views.notas, name='home'),
    path('moveis/',views.notas, name='moveis'),
    path('correcoes/',views.correcao, name='correcao'),
    path('correcoes/<int:id>/',views.vercorrecao, name='correcaoind'),
    path('post/',views.edit, name='post'),
    path('novacorrecao/',views.novacorrecao, name='novacorrecao'),
]
