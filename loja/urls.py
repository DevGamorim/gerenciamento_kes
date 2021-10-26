from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'loja'

urlpatterns =[
    path('', views.conferencia, name='irloja'),
    path('notas/',views.notas, name='notas'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)