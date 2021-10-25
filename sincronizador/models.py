from django.db import models

from produtos.models import Produto
# Create your models here.

class Sinc_Config(models.Model):
    SC_ID = models.AutoField(primary_key=True)
    SC_Nome = models.CharField(max_length=100)
    SC_Key = models.CharField(max_length=300)
    SC_ip = models.CharField(max_length=100)
    SC_TempoExecucao = models.IntegerField()

    def __str__(self):
        return str(self.SC_Nome)

class Sinc_log(models.Model):

    SL_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    SL_Nome =  models.CharField(max_length=100)
    SL_GetOrigem = models.CharField(max_length=100, unique=False, null=True)
    SL_PostSaida = models.CharField(max_length=100, unique=False, null=True)
    SL_ProdutoID = models.ForeignKey(Produto, on_delete=models.CASCADE)
    SL_PrecoDe = models.FloatField()
    SL_PrecoPor = models.FloatField()
    SL_Estoque = models.IntegerField()
    SL_user = models.CharField(max_length=100, unique=False, null=True)
    SL_view = models.BooleanField(unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.SL_Nome)

class Sinc_Accs(models.Model):
    SA_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    SA_Nome = models.CharField(max_length=100)
    SA_Senha = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.SA_Nome)

class Sinc_open(models.Model):
    SO_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    SO_status = models.BooleanField()

    class Meta:
        managed=False


class Sinc_view(models.Model):
    SV_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    SV_Site = models.BooleanField()
    SV_Omni = models.BooleanField()
    SV_Master = models.BooleanField()
