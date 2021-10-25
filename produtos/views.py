#Imports Django
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
#Import Models
from sincronizador.models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view
from produtos.models import Produto, Preco_Portal, Confere_Preco_log, Nota, Correcoes, Correcoes_log
from vendas.models import Venda
from background_task.models import Task
#Import for apps
from background_task import background
import requests
import json
import yaml
from datetime import datetime
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
from time import sleep
import json
from html.parser import HTMLParser
from django import db
import html
from lxml import etree
from lxml import html
import socket
from requests import get
from datetime import date
import pyrebase
import yaml

# Create your views here.
from .models import Produtos_Arrigo
from .models import opcao_cor,opcao_verniz,opcao_tipo_tinta,opcao_escala_cor,opcao_material,opcao_material_especura
from .models import opcao_material_suporte,opcao_material_pintura_suporte,opcao_material_acabamento,opcao_localizacao
from .models import opcao_tipo_suporte,opcao_possui_pes,opcao_tipo_fixacao,opcao_envio

Moveis = ''

@method_decorator(login_required, name='dispatch')
class HomePageView(TemplateView):
    template_name = 'home.html'


@login_required
def todososmoveis(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        moveis = []
        movel = Produtos_Arrigo.objects.filter(PM_sku=PA_sku).order_by("PA_sku")
        moveis.append(movel)
        
    else:
        moveis = Produtos_Arrigo.objects.all().order_by("PA_sku")
        print(moveis)

    return render(request,"produto/todos_moveis.html",{"moveis":moveis})


@login_required
def vermovel(request, id):
    movel = get_object_or_404(Produtos_Arrigo, pk=id)
    return render(request,"produto/produto_movel.html",{"moveis":movel})


@login_required
def criarmovel(request):
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)

        PA_sku = tudo['PA_sku']
        PA_modelo = tudo['PA_modelo']
        PA_titulo = tudo['PA_titulo']
        PA_custo = tudo['PA_custo']
        PA_preco_venda = tudo['PA_preco_venda']
        PA_peso_suportado = tudo['PA_peso_suportado']
        PA_capacidade_garrafas = tudo['PA_capacidade_garrafas']
        PA_capacidade_tacas = tudo['PA_capacidade_tacas']
        PA_quantidade_prateleiras = tudo['PA_quantidade_prateleiras']
        PA_quantidade_suportes = tudo['PA_quantidade_suportes']
        PA_quantidade_gavetas = tudo['PA_quantidade_gavetas']
        PA_capacidade_copos = tudo['PA_capacidade_copos']
        PA_quantidade_parafusos_fixacao = tudo['PA_quantidade_parafusos_fixacao']
        PA_peso = tudo['PA_peso']
        PA_medida_externa_altura = tudo['PA_medida_externa_altura']
        PA_medida_externa_largura = tudo['PA_medida_externa_largura']
        PA_medida_externa_profundidade = tudo['PA_medida_externa_profundidade']
        PA_medidas_internas = tudo['PA_medidas_internas']

        opcao_vernizs = tudo['opcao_verniz']
        opcao_tipo_tintas = tudo['opcao_tipo_tinta']
        opcao_tipo_suportes = tudo['opcao_tipo_suporte']
        opcao_tipo_fixacaos = tudo['opcao_tipo_fixacao']
        opcao_possui_pess = tudo['opcao_possui_pes']
        opcao_material_suportes = tudo['opcao_material_suporte']
        opcao_material_pintura_suportes = tudo['opcao_material_pintura_suporte']
        opcao_material_especuras = tudo['opcao_material_especura']
        opcao_material_acabamentos = tudo['opcao_material_acabamento']
        opcao_materials = tudo['opcao_material']
        opcao_localizacaos = tudo['opcao_localizacao']
        opcao_escala_cors = tudo['opcao_escala_cor']
        opcao_envios = tudo['opcao_envio']
        opcao_cors = tudo['opcao_cor']

        novo_opcao_verniz = tudo['novo_opcao_verniz']
        novo_opcao_tipo_tinta = tudo['novo_opcao_tipo_tinta']
        novo_opcao_tipo_suporte = tudo['novo_opcao_tipo_suporte']
        novo_opcao_tipo_fixacao = tudo['novo_opcao_tipo_fixacao']
        novo_opcao_possui_pes = tudo['novo_opcao_possui_pes']
        novo_opcao_material_suporte = tudo['novo_opcao_material_suporte']
        novo_opcao_material_pintura_suporte = tudo['novo_opcao_material_pintura_suporte']
        novo_opcao_material_especura = tudo['novo_opcao_material_especura']
        novo_opcao_material_acabamento = tudo['novo_opcao_material_acabamento']
        novo_opcao_material = tudo['novo_opcao_material']
        novo_opcao_localizacao = tudo['novo_opcao_localizacao']
        novo_opcao_escala_cor = tudo['novo_opcao_escala_cor']
        novo_opcao_envio = tudo['novo_opcao_envio']
        novo_opcao_cor = tudo['novo_opcao_cor']

        skuh = str(PA_sku)

        PA_imagem1 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "1.jpg"
        PA_imagem2 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "2.jpg"
        PA_imagem3 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "3.jpg"
        PA_imagem4 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "4.jpg"
        PA_imagem5 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "5.jpg"
        PA_imagem6 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "6.jpg"
        PA_imagem7 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "7.jpg"
        PA_imagem8 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "8.jpg"
        PA_imagem9 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "9.jpg"
        PA_imagem10 = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "10.jpg"

        if len(novo_opcao_cor) >= 1:
            lista = opcao_cor.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_cor).upper():
                    comparador = "igual"
                    opcao_cors = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_cors = novo_opcao_cor
            if comparador == "diferente":
                criador = opcao_cor.objects.create(valor=novo_opcao_cor)

        if len(novo_opcao_verniz) >= 1:
            lista = opcao_verniz.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_verniz).upper():
                    comparador = "igual"
                    opcao_vernizs = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_vernizs = novo_opcao_verniz
            if comparador == "diferente":
                criador = opcao_verniz.objects.create(valor=novo_opcao_verniz)
        
        if len(novo_opcao_tipo_tinta) >= 1:
            lista = opcao_tipo_tinta.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_tipo_tinta).upper():
                    comparador = "igual"
                    opcao_tipo_tintas = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_tipo_tintas = novo_opcao_tipo_tinta
            if comparador == "diferente":
                criador = opcao_tipo_tinta.objects.create(valor=novo_opcao_tipo_tinta)
        
        if len(novo_opcao_escala_cor) >= 1:
            lista = opcao_escala_cor.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_escala_cor).upper():
                    comparador = "igual"
                    opcao_escala_cors = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_escala_cors = novo_opcao_escala_cor
            if comparador == "diferente":
                criador = opcao_escala_cor.objects.create(valor=novo_opcao_escala_cor)

        if len(novo_opcao_material) >= 1:
            lista = opcao_material.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_material).upper():
                    comparador = "igual"
                    opcao_materials = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_materials = novo_opcao_material
            if comparador == "diferente":
                criador = opcao_material.objects.create(valor=novo_opcao_material)

        if len(novo_opcao_material_especura) >= 1:
            lista = opcao_material_especura.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_material_especura).upper():
                    comparador = "igual"
                    opcao_material_especuras = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_material_especuras = novo_opcao_material_especura
            if comparador == "diferente":
                criador = opcao_material_especura.objects.create(valor=novo_opcao_material_especura)

        if len(novo_opcao_material_suporte) >= 1:
            lista = opcao_material_suporte.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_material_suporte).upper():
                    comparador = "igual"
                    opcao_material_suportes = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_material_suportes = novo_opcao_material_suporte
            if comparador == "diferente":
                criador = opcao_material_suporte.objects.create(valor=novo_opcao_material_suporte)

        if len(novo_opcao_material_pintura_suporte) >= 1:
            lista = opcao_material_pintura_suporte.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_material_pintura_suporte).upper():
                    comparador = "igual"
                    opcao_material_pintura_suportes = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_material_pintura_suportes = novo_opcao_material_pintura_suporte
            if comparador == "diferente":
                criador = opcao_material_pintura_suporte.objects.create(valor=novo_opcao_material_pintura_suporte)

        if len(novo_opcao_material_acabamento) >= 1:
            lista = opcao_material_acabamento.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_material_acabamento).upper():
                    comparador = "igual"
                    opcao_material_acabamentos = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_material_acabamentos = novo_opcao_material_acabamento
            if comparador == "diferente":
                criador = opcao_material_acabamento.objects.create(valor=novo_opcao_material_acabamento)
        
        if len(novo_opcao_localizacao) >= 1:
            lista = opcao_localizacao.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_localizacao).upper():
                    comparador = "igual"
                    opcao_localizacaos = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_localizacaos = novo_opcao_localizacao
            if comparador == "diferente":
                criador = opcao_localizacao.objects.create(valor=novo_opcao_localizacao)

        if len(novo_opcao_tipo_suporte) >= 1:
            lista = opcao_tipo_suporte.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_tipo_suporte).upper():
                    comparador = "igual"
                    opcao_tipo_suportes = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_tipo_suportes = novo_opcao_tipo_suporte
            if comparador == "diferente":
                criador = opcao_tipo_suporte.objects.create(valor=novo_opcao_tipo_suporte)

        if len(novo_opcao_possui_pes) >= 1:
            lista = opcao_possui_pes.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_possui_pes).upper():
                    comparador = "igual"
                    opcao_possui_pess = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_possui_pess = novo_opcao_possui_pes
            if comparador == "diferente":
                criador = opcao_possui_pes.objects.create(valor=novo_opcao_possui_pes)

        if len(novo_opcao_tipo_fixacao) >= 1:
            lista = opcao_tipo_fixacao.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_tipo_fixacao).upper():
                    comparador = "igual"
                    opcao_tipo_fixacaos = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_tipo_fixacaos = novo_opcao_tipo_fixacao
            if comparador == "diferente":
                criador = opcao_tipo_fixacao.objects.create(valor=novo_opcao_tipo_fixacao)

        if len(novo_opcao_envio) >= 1:
            lista = opcao_envio.objects.all()
            for n in range(0,len(lista)):
                vetor = lista[n]
                if str(vetor.valor).upper() == str(novo_opcao_envio).upper():
                    comparador = "igual"
                    opcao_envios = vetor.valor
                    break
                else:
                    comparador = "diferente"
                    opcao_envios = novo_opcao_envio
            if comparador == "diferente":
                criador = opcao_envio.objects.create(valor=novo_opcao_envio)
        
        novo = Produtos_Arrigo.objects.create(
            PA_sku=PA_sku,
            PA_modelo=PA_modelo, 
            PA_titulo=PA_titulo, 
            PA_custo=PA_custo, 
            PA_preco_venda=PA_preco_venda, 
            PA_peso_suportado=PA_peso_suportado, 
            PA_capacidade_garrafas=PA_capacidade_garrafas, 
            PA_capacidade_tacas=PA_capacidade_tacas, 
            PA_capacidade_copos=PA_capacidade_copos,
            PA_quantidade_prateleiras=PA_quantidade_prateleiras, 
            PA_quantidade_suportes=PA_quantidade_suportes, 
            PA_quantidade_gavetas=PA_quantidade_gavetas, 
            PA_quantidade_parafusos_fixacao=PA_quantidade_parafusos_fixacao, 
            PA_peso=PA_peso, 
            PA_medida_externa_altura=PA_medida_externa_altura, 
            PA_medida_externa_largura=PA_medida_externa_largura, 
            PA_medida_externa_profundidade=PA_medida_externa_profundidade, 
            PA_medidas_internas=PA_medidas_internas, 
            PA_verniz=opcao_vernizs, 
            PA_tipo_tinta=opcao_tipo_tintas, 
            PA_tipo_suporte=opcao_tipo_suportes, 
            PA_tipo_fixacao=opcao_tipo_fixacaos, 
            PA_possui_pes=opcao_possui_pess, 
            PA_material_suporte=opcao_material_suportes, 
            PA_material_pintura_suporte=opcao_material_pintura_suportes, 
            PA_material_especura=opcao_material_especuras, 
            PA_material_acabamento=opcao_material_acabamentos, 
            PA_material=opcao_materials, 
            PA_localizacao=opcao_localizacaos, 
            PA_escala_cor=opcao_escala_cors, 
            PA_envio=opcao_envios, 
            PA_cor=opcao_cors,
            PA_imagem1=PA_imagem1,
            PA_imagem2=PA_imagem2,
            PA_imagem3=PA_imagem3,
            PA_imagem4=PA_imagem4,
            PA_imagem5=PA_imagem5,
            PA_imagem6=PA_imagem6,
            PA_imagem7=PA_imagem7,
            PA_imagem8=PA_imagem8,
            PA_imagem9=PA_imagem9,
            PA_imagem10=PA_imagem10,
            )

        moveis = Produtos_Arrigo.objects.all().order_by("PA_sku")
        return render(request,"produto/todos_moveis.html",{"moveis":moveis})
    else:
        cor_opcao = opcao_cor.objects.all().order_by('valor')
        verniz_opcao = opcao_verniz.objects.all().order_by('valor')
        tipo_tinta_opcao = opcao_tipo_tinta.objects.all().order_by('valor')
        escala_cor_opcao = opcao_escala_cor.objects.all().order_by('valor')
        material_opcao = opcao_material.objects.all().order_by('valor')
        material_especura_opcao = opcao_material_especura.objects.all().order_by('valor')
        material_suporte_opcao = opcao_material_suporte.objects.all().order_by('valor')
        material_pintura_suporte_opcao = opcao_material_pintura_suporte.objects.all().order_by('valor')
        material_acabamento_opcao = opcao_material_acabamento.objects.all().order_by('valor')
        localizacao_opcao = opcao_localizacao.objects.all().order_by('valor')
        tipo_suporte_opcao = opcao_tipo_suporte.objects.all().order_by('valor')
        possui_pes_opcao = opcao_possui_pes.objects.all().order_by('valor')
        tipo_fixacao_opcao = opcao_tipo_fixacao.objects.all().order_by('valor')
        envio_opcao = opcao_envio.objects.all().order_by('valor')

        return render(request,"produto/novomovel.html",{'cor_opcao':cor_opcao,
            'verniz_opcao':verniz_opcao,
            'tipo_tinta_opcao':tipo_tinta_opcao,
            'escala_cor_opcao':escala_cor_opcao,
            'material_opcao':material_opcao,
            'material_especura_opcao':material_especura_opcao,
            'material_suporte_opcao':material_suporte_opcao,
            'material_pintura_suporte_opcao':material_pintura_suporte_opcao,
            'material_pintura_suporte_opcao':material_pintura_suporte_opcao,
            'material_acabamento_opcao':material_acabamento_opcao,
            'localizacao_opcao':localizacao_opcao,
            'tipo_suporte_opcao':tipo_suporte_opcao,
            'possui_pes_opcao':possui_pes_opcao,
            'tipo_fixacao_opcao':tipo_fixacao_opcao,
            'envio_opcao':envio_opcao,
        })


@login_required
def editarmovel(request):
    lista_produs = []
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        tipo = tudo['tipo']
        print(tudo)
        moveis = Produtos_Arrigo.objects.get(pk=str(tudo['id']))
        return render(request,"produto/editarmovel.html",{"moveis":moveis})
    else:
        moveis = Produtos_Arrigo.objects.all().order_by("PA_sku")
        return render(request,"produto/todos_moveis.html",{"moveis":moveis})