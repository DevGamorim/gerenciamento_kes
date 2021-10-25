from django.urls import path

from . import views

app_name = 'loja'

urlpatterns =[
    path('', views.conferencia, name='irloja'),
    path('notas/',views.notas, name='notas'),
]