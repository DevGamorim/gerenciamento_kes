from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'sinc'

urlpatterns =[
    #path('', views.HomePageView.as_view(), name='home' ),
    path('', views.sinc, name='irsinc'),
    path('teste/',views.teste, name='teste'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)