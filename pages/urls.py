from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'pages'

urlpatterns =[
    path('', views.HomePageView.as_view(), name='home' ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)