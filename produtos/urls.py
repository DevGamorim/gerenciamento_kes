from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'produtos'

urlpatterns =[
    path('', views.HomePageView.as_view(), name='home' ),
    path('moveis/', views.todososmoveis, name="moveis"),
    path('editarmovel/', views.editarmovel, name="editarmovel"),
    path('moveis/<int:id>/', views.vermovel, name='vermovel'),
    path('correcao/', views.todososmoveis, name='vermovel'),
    path('criarprodutos/',views.criarmovel, name="criarmovel")
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)