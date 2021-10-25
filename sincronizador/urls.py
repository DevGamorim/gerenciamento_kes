from django.urls import path

from . import views

app_name = 'sinc'

urlpatterns =[
    #path('', views.HomePageView.as_view(), name='home' ),
    path('', views.sinc, name='irsinc'),
    path('teste/',views.teste, name='teste'),
]