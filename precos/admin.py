from django.contrib import admin
from .models import Comissoes, Preco_Faixa, Precificacao_log, Custo_log
# Register your models here.

admin.site.register(Comissoes)
admin.site.register(Preco_Faixa)
admin.site.register(Precificacao_log)
admin.site.register(Custo_log)