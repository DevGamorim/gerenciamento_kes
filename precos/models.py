from django.db import models
from django.conf import settings
import jsonfield



class Comissoes(models.Model):
    CS_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    CS_Nome = models.CharField(max_length=100,unique=False, null=True)
    CS_Custo_Adm_portal = models.FloatField(unique=False, null=True)
    CS_Custo_Adm_site = models.FloatField(unique=False, null=True)
    CS_Impostos = models.FloatField(unique=False, null=True)
    CS_Comissao_site = models.FloatField(unique=False, null=True)

    CS_Amazon_ID = models.IntegerField(null=True, unique=False)
    CS_Amazon_Comissao = models.FloatField(unique=False, null=True)

    CS_B2W_ALK_ID = models.IntegerField(null=True, unique=False)
    CS_B2W_ALK_Comissao = models.FloatField(unique=False, null=True)

    CS_B2W_GEA_ID = models.IntegerField(null=True, unique=False)
    CS_B2W_GEA_Comissao = models.FloatField(unique=False, null=True)

    CS_B2W_JCMA_ID = models.IntegerField(null=True, unique=False)
    CS_B2W_JCMA_Comissao = models.FloatField(unique=False, null=True)   

    CS_B2W_KC_ID = models.IntegerField(null=True, unique=False)
    CS_B2W_KC_Comissao = models.FloatField(unique=False, null=True)

    CS_Carrefour_ALK_ID = models.IntegerField(null=True, unique=False)
    CS_Carrefour_ALK_Comissao = models.FloatField(unique=False, null=True)

    CS_Carrefour_GEA_ID = models.IntegerField(null=True, unique=False)
    CS_Carrefour_GEA_Comissao = models.FloatField(unique=False, null=True)

    CS_Centauro_ALK_ID = models.IntegerField(null=True, unique=False)
    CS_Centauro_ALK_Comissao = models.FloatField(unique=False, null=True)

    CS_Cnova_KES_ID = models.IntegerField(null=True, unique=False)
    CS_Cnova_KES_Comissao = models.FloatField(unique=False, null=True)

    CS_MM_KES_ID = models.IntegerField(null=True, unique=False)
    CS_MM_KES_Comissao = models.FloatField(unique=False, null=True)

    CS_Magalu_GEA_ID = models.IntegerField(null=True, unique=False)
    CS_Magalu_GEA_Comissao = models.FloatField(unique=False, null=True)

    CS_Magalu_KC_ID = models.IntegerField(null=True, unique=False)
    CS_Magalu_KC_Comissao = models.FloatField(unique=False, null=True)

    CS_Netshoes_ALK_ID = models.IntegerField(null=True, unique=False)
    CS_Netshoes_ALK_Comissao = models.FloatField(unique=False, null=True)

    CS_Netshoes_KES_ID = models.IntegerField(null=True, unique=False)
    CS_Netshoes_KES_Comissao = models.FloatField(unique=False, null=True)

    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)


    def __str__(self):
        return self.CS_Nome


class Preco_Faixa(models.Model):
    PF_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    PF_None = models.CharField(max_length=100,unique=False, null=True)
    PF_0_a_4_99 = models.FloatField(unique=False, null=True)
    PF_5_a_14_99 = models.FloatField(unique=False, null=True)
    PF_15_a_29_99 = models.FloatField(unique=False, null=True)
    PF_30_a_49_99 = models.FloatField(unique=False, null=True)
    PF_50_a_79_99 = models.FloatField(unique=False, null=True)
    PF_80_a_119_99 =models.FloatField(unique=False, null=True)
    PF_120_a_149_99 = models.FloatField(unique=False, null=True)
    PF_150_a_199_99 = models.FloatField(unique=False, null=True)
    PF_200_a_249_99 = models.FloatField(unique=False, null=True)
    PF_250_a_299_99 = models.FloatField(unique=False, null=True)
    PF_300_a_349_99 = models.FloatField(unique=False, null=True)
    PF_350_a_399_99 = models.FloatField(unique=False, null=True)
    PF_400_a_449_99 = models.FloatField(unique=False, null=True)
    PF_450_a_549_99 = models.FloatField(unique=False, null=True)
    PF_550_a_649_99 = models.FloatField(unique=False, null=True)
    PF_650_a_749_99 = models.FloatField(unique=False, null=True)
    PF_750_a_899_99 = models.FloatField(unique=False, null=True)
    PF_900_a_999_99 = models.FloatField(unique=False, null=True)
    PF_1000_a_1499_99 = models.FloatField(unique=False, null=True)
    PF_1500_a_1999_99 = models.FloatField(unique=False, null=True)
    PF_2000_a_2499_99 = models.FloatField(unique=False, null=True)
    PF_2500_a_2999_99 = models.FloatField(unique=False, null=True)
    PF_maior_3000 = models.FloatField(unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

    def __str__(self):
        return self.PF_None


class Precificacao_log(models.Model):
    PL_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    #PL_Sku = models.ForeignKey(Produto, on_delete=models.CASCADE)
    PL_Sku = models.CharField(max_length=100,unique=False, null=True)  
    PL_nome = models.CharField(max_length=100,unique=False, null=True)    
    PL_Classificacao_anterior = models.FloatField(unique=False, null=True)
    PL_Classificacao_novo = models.FloatField(unique=False, null=True)
    PL_Custo_adm_anterior = models.FloatField(unique=False, null=True)
    PL_Custo_adm_novo = models.FloatField(unique=False, null=True)
    PL_Preco_de_anterior = models.FloatField(unique=False, null=True)
    PL_Preco_de_novo = models.FloatField(unique=False, null=True)
    PL_Preco_por_anterior = models.FloatField(unique=False, null=True)
    PL_Preco_por_novo = models.FloatField(unique=False, null=True)
    PL_User = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

    def __str__(self):
        return self.PL_nome


class Custo_log(models.Model):
    CL_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    #PL_Sku = models.ForeignKey(Produto, on_delete=models.CASCADE)
    CL_Sku = models.CharField(max_length=100,unique=False, null=True)  
    CL_nome = models.CharField(max_length=100,unique=False, null=True)    
    CL_valor_antigo = models.FloatField(unique=False, null=True)
    CL_valorr_novo = models.FloatField(unique=False, null=True)
    CL_user = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
    updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

    def __str__(self):
        return self.CL_nome




