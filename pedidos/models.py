from django.db import models
from auditlog.registry import auditlog
from django.conf import settings
import jsonfield
# Create your models here.

class Pedido(models.Model):
    PD_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    PD_identificacao = models.CharField(max_length=100,unique=False, null=True)
    PD_status = models.CharField(max_length=11,unique=False, null=True)
    PD_excluido = models.BooleanField(unique=False, null=True)
    PD_finalizado = models.BooleanField(unique=False, null=True)

    PD_quant_sku = models.IntegerField(unique=False, null=True)

    PD_portal = models.CharField(max_length=100,unique=False, null=True)
    PD_coleta = models.CharField(max_length=20,unique=False, null=True)
    PD_dia_finalizar = models.CharField(max_length=20,unique=False, null=True)
    PD_dia_hora_entrega = models.DateField(unique=False, null=True)
    PD_aviso_novo = models.BooleanField(unique=False, null=True)
    PD_valor_total = models.FloatField(unique=False, null=True)

    PD_full = models.BooleanField(unique=False, null=True)

    PD_sku1 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant1 = models.IntegerField(unique=False, null=True)
    PD_obs1 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco1 = models.FloatField(unique=False, null=True)
    PD_titulo_produto1 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto1 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto1 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto1 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku2 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant2 =models.IntegerField(unique=False, null=True)
    PD_obs2 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco2 = models.FloatField(unique=False, null=True)
    PD_titulo_produto2 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto2 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto2 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto2 = models.CharField(max_length=200,unique=False, null=True)
    
    PD_sku3 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant3 =models.IntegerField(unique=False, null=True)
    PD_obs3 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco3 = models.FloatField(unique=False, null=True)
    PD_titulo_produto3 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto3 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto3 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto3 = models.CharField(max_length=200,unique=False, null=True)
    
    PD_sku4 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant4 =models.IntegerField(unique=False, null=True)
    PD_obs4 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco4 = models.FloatField(unique=False, null=True)
    PD_titulo_produto4 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto4 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto4 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto4 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku5 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant5 =models.IntegerField(unique=False, null=True)
    PD_obs5 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco5 = models.FloatField(unique=False, null=True)
    PD_titulo_produto5 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto5 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto5 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto5 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku6 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant6 =models.IntegerField(unique=False, null=True)
    PD_obs6 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco6 = models.FloatField(unique=False, null=True)
    PD_titulo_produto6 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto6 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto6 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto6 = models.CharField(max_length=200,unique=False, null=True)
    
    PD_sku7 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant7 =models.IntegerField(unique=False, null=True)
    PD_obs7 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco7 = models.FloatField(unique=False, null=True)
    PD_titulo_produto7 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto7 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto7 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto7 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku8 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant8 =models.IntegerField(unique=False, null=True)
    PD_obs8 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco8 = models.FloatField(unique=False, null=True)
    PD_titulo_produto8 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto8 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto8 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto8 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku9 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant9 =models.IntegerField(unique=False, null=True)
    PD_obs9 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco9 = models.FloatField(unique=False, null=True)
    PD_titulo_produto9 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto9 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto9 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto9 = models.CharField(max_length=200,unique=False, null=True)

    PD_sku10 = models.CharField(max_length=20,unique=False, null=True)
    PD_quant10 =models.IntegerField(unique=False, null=True)
    PD_obs10 = models.CharField(max_length=200,unique=False, null=True)
    PD_preco10 = models.FloatField(unique=False, null=True)
    PD_titulo_produto10 = models.CharField(max_length=200,unique=False, null=True)
    PD_cor_produto10 = models.CharField(max_length=50,unique=False, null=True)
    PD_material_produto10 = models.CharField(max_length=50,unique=False, null=True)
    PD_imagem_produto10 = models.CharField(max_length=200,unique=False, null=True)

    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
    user_created = models.CharField(max_length=200,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
    user_updated = models.CharField(max_length=200,unique=False, null=True)

    def __str__(self):
        return str(self.PD_identificacao)


class Log_Pedidos(models.Model):
    LP_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    LP_Pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    LP_campo = models.CharField(max_length=200,unique=False, null=True)
    LP_novo_valor = models.CharField(max_length=200,unique=False, null=True)
    LP_antigo_valor = models.CharField(max_length=200,unique=False, null=True)
    LP_user = models.CharField(max_length=100,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)

    def __str__(self):
        return str(self.LP_Pedido)

class Estoque_arrigo(models.Model):
    EA_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    EA_sku = models.CharField(max_length=50,unique=False, null=True)
    EA_titulo = models.CharField(max_length=200,unique=False, null=True)
    EA_estoque_arrigo =models.IntegerField(unique=False, null=True)
    EA_estoque_koala =models.IntegerField(unique=False, null=True)
    EA_estoque_total = models.IntegerField(unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)

    def __str__(self):
        return str(self.EA_sku)
    
class Log_estoques(models.Model):
    LE_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    LE_sku = models.ForeignKey(Estoque_arrigo, on_delete=models.CASCADE)
    LE_campo = models.CharField(max_length=200,unique=False, null=True)
    LE_novo_valor = models.CharField(max_length=200,unique=False, null=True)
    LE_antigo_valor = models.CharField(max_length=200,unique=False, null=True)
    LE_user = models.CharField(max_length=100,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)

    def __str__(self):
        return str(self.LE_sku)