from django.contrib import admin

# Register your models here.
from .models import Pedido, Log_Pedidos, Estoque_arrigo, Log_estoques

admin.site.register(Pedido)
admin.site.register(Log_Pedidos)
admin.site.register(Estoque_arrigo)
admin.site.register(Log_estoques)