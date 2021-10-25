from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    Us_Status = (
        ('ativo','Ativo'),
        ('inativo','Inativo'),
    )
    Us_Setor = (
        ('administracao', 'Administração'),
        ('catalogo', 'Catalogo'),
        ('comercial', 'Comercial'),
        ('compras', 'Compras'),
        ('expedicao', 'Expedição'),
        ('financeiro', 'Financeiro'),
        ('logistica', 'Logistica'),
        ('loja', 'Loja'),
        ('marketing', 'Marketing'),
        ('prevenda', 'Pré-Venda'),
        ('producao', 'Producao'),
        ('sac', 'Sac'),
        ('sinc', 'Sincronizador'),
        ('ti', 'T.I'),
    )
    Us_Status = models.CharField(
        max_length=7,
        choices = Us_Status,
    )
    Us_Setor = models.CharField(
        max_length=13,
        choices = Us_Setor,
    )