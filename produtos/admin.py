from django.contrib import admin

# Register your models here.
from .models import Produto, Preco_Portal, Confere_Preco_log, Produto_Precificacao, Fornecedores, Nota, Kit, Correcoes, Correcoes_log,Produtos_Arrigo

from .models import opcao_cor,opcao_verniz,opcao_tipo_tinta,opcao_escala_cor,opcao_material,opcao_material_especura
from .models import opcao_material_suporte,opcao_material_pintura_suporte,opcao_material_acabamento,opcao_localizacao
from .models import opcao_tipo_suporte,opcao_possui_pes,opcao_tipo_fixacao,opcao_envio

#Apps
admin.site.register(Produto)
admin.site.register(Preco_Portal)
admin.site.register(Confere_Preco_log)
admin.site.register(Produto_Precificacao)
admin.site.register(Fornecedores)
admin.site.register(Nota)
admin.site.register(Kit)
admin.site.register(Produtos_Arrigo)
admin.site.register(Correcoes)
admin.site.register(Correcoes_log)

## Atributos de Produtos_Arrigo

admin.site.register(opcao_cor)
admin.site.register(opcao_verniz)
admin.site.register(opcao_tipo_tinta)
admin.site.register(opcao_escala_cor)
admin.site.register(opcao_material)
admin.site.register(opcao_material_especura)
admin.site.register(opcao_material_suporte)
admin.site.register(opcao_material_pintura_suporte)
admin.site.register(opcao_material_acabamento)
admin.site.register(opcao_localizacao)
admin.site.register(opcao_tipo_suporte)
admin.site.register(opcao_possui_pes)
admin.site.register(opcao_tipo_fixacao)
admin.site.register(opcao_envio)