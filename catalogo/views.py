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


@login_required
def notas(request):
    nfs =  Nota.objects.filter(NT_visualizado=False)
    produto = {}
    retorno = []
    if request.method == 'POST':
        for n in range(0,len(nfs)):
            nota = nfs[n]
            nota.NT_visualizado = True
            nota.save()
    else:
        for n in range(0,len(nfs)):
            nota = nfs[n]
            numero = nota.NT_Num_NF
            forn = nota.NT_fornecedor
            produtos = nota.NT_produtos
            for nn in range(0,len(produtos)):
                skuh = produtos[nn]
                if str(skuh[:2]) == "KT":
                    continue
                else:
                    prods = Produto.objects.get(Pro_Sku=skuh)
                    link = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "1.jpg"
                    produto['nota'] = numero
                    produto['forne'] = str(forn).replace("A - ","")
                    produto['Pro_Sku'] = skuh
                    produto['link'] = link
                    produto['Pro_Nome'] = prods.Pro_Nome
                    produto['Pro_Loja'] = prods.Pro_Loja
                    produto['Pro_PrecoVenda'] = prods.Pro_PrecoVenda
                    retorno.append(dict(produto))

        retorno = sorted(retorno, key=lambda k: k['nota'])
    return render(request,'loja/nota_conferencia.html',{'lista_skus':retorno})


@login_required
def correcao(request):
    corre = Correcoes.objects.filter(CR_status="Andamento").order_by('CR_prioridade')
    for n in range(0,len(corre)):
        print(corre[n].CR_status)
        if corre[n].CR_status == True:            
            corre[n].delete()
            n = n -1 

    return render(request,'produto/correcoes.html',{'correcoes':corre})


@login_required
def vercorrecao(request, id):
    corre = get_object_or_404(Correcoes, pk=id)
    if request.method == 'POST':
        tudo = request.POST.copy()
        print(tudo)
        corre = get_object_or_404(Correcoes, pk=id)
    return render(request,"produto/vercorrecao.html",{"correcoes":corre})


@login_required
def edit(request):
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)
        sku = tudo['sku']
        corre = Correcoes.objects.get(CR_sku = str(sku))
        CR_portal_ML_alaok = tudo['CR_portal_ML_alaok']
        if CR_portal_ML_alaok != corre.CR_portal_ML_alaok:
            corre.CR_portal_ML_alaok = CR_portal_ML_alaok

        CR_portal_ML_gea = tudo['CR_portal_ML_gea']
        if CR_portal_ML_gea != corre.CR_portal_ML_gea:
            corre.CR_portal_ML_gea = CR_portal_ML_gea
            
        CR_portal_ML_kes = tudo['CR_portal_ML_kes']
        if CR_portal_ML_kes != corre.CR_portal_ML_kes:
            corre.CR_portal_ML_kes = CR_portal_ML_kes
            
        CR_portal_ML_arrigo = tudo['CR_portal_ML_arrigo']
        if CR_portal_ML_arrigo != corre.CR_portal_ML_arrigo:
            corre.CR_portal_ML_arrigo = CR_portal_ML_arrigo
            
        CR_portal_Magalu_gea = tudo['CR_portal_Magalu_gea']
        if CR_portal_Magalu_gea != corre.CR_portal_Magalu_gea:
            corre.CR_portal_Magalu_gea = CR_portal_Magalu_gea
            
        CR_portal_Magalu_kes = tudo['CR_portal_Magalu_kes']
        if CR_portal_Magalu_kes != corre.CR_portal_Magalu_kes:
            corre.CR_portal_Magalu_kes = CR_portal_Magalu_kes
            
        CR_portal_Magalu_kc = tudo['CR_portal_Magalu_kc']
        if CR_portal_Magalu_kc != corre.CR_portal_Magalu_kc:
            corre.CR_portal_Magalu_kc = CR_portal_Magalu_kc
            
        CR_portal_Magalu_arrigo = tudo['CR_portal_Magalu_arrigo']
        if CR_portal_Magalu_arrigo != corre.CR_portal_Magalu_arrigo:
            corre.CR_portal_Magalu_arrigo = CR_portal_Magalu_arrigo
            
        CR_portal_carrefour_alaok = tudo['CR_portal_carrefour_alaok']
        if CR_portal_carrefour_alaok != corre.CR_portal_carrefour_alaok:
            corre.CR_portal_carrefour_alaok = CR_portal_carrefour_alaok
            
        CR_portal_carrefour_gea = tudo['CR_portal_carrefour_gea']
        if CR_portal_carrefour_gea != corre.CR_portal_carrefour_gea:
            corre.CR_portal_carrefour_gea = CR_portal_carrefour_gea
            
        CR_portal_carrefour_arrigo = tudo['CR_portal_carrefour_arrigo']
        if CR_portal_carrefour_arrigo != corre.CR_portal_carrefour_arrigo:
            corre.CR_portal_carrefour_arrigo = CR_portal_carrefour_arrigo
            
        CR_portal_netshoes_alk = tudo['CR_portal_netshoes_alk']
        if CR_portal_netshoes_alk != corre.CR_portal_netshoes_alk:
            corre.CR_portal_netshoes_alk = CR_portal_netshoes_alk
            
        CR_portal_netshoes_kes = tudo['CR_portal_netshoes_kes']
        if CR_portal_netshoes_kes != corre.CR_portal_netshoes_kes:
            corre.CR_portal_netshoes_kes = CR_portal_netshoes_kes
            
        CR_portal_olist_gea = tudo['CR_portal_olist_gea']
        if CR_portal_olist_gea != corre.CR_portal_olist_gea:
            corre.CR_portal_olist_gea = CR_portal_olist_gea
            
        CR_portal_olist_arrigo = tudo['CR_portal_olist_arrigo']
        if CR_portal_olist_arrigo != corre.CR_portal_olist_arrigo:
            corre.CR_portal_olist_arrigo = CR_portal_olist_arrigo
            
        CR_portal_madeiramadeira_kes = tudo['CR_portal_madeiramadeira_kes']
        if CR_portal_madeiramadeira_kes != corre.CR_portal_madeiramadeira_kes:
            corre.CR_portal_madeiramadeira_kes = CR_portal_madeiramadeira_kes
            
        CR_portal_madeiramadeira_arrigo = tudo['CR_portal_madeiramadeira_arrigo']
        if CR_portal_madeiramadeira_arrigo != corre.CR_portal_madeiramadeira_arrigo:
            corre.CR_portal_madeiramadeira_arrigo = CR_portal_madeiramadeira_arrigo
            
        CR_portal_amazon_kes = tudo['CR_portal_amazon_kes']
        if CR_portal_amazon_kes != corre.CR_portal_amazon_kes:
            corre.CR_portal_amazon_kes = CR_portal_amazon_kes
            
        CR_portal_amazon_kc = tudo['CR_portal_amazon_kc']
        if CR_portal_amazon_kc != corre.CR_portal_amazon_kc:
            corre.CR_portal_amazon_kc = CR_portal_amazon_kc
            
        CR_portal_amazon_arrigo = tudo['CR_portal_amazon_arrigo']
        if CR_portal_amazon_arrigo != corre.CR_portal_amazon_arrigo:
            corre.CR_portal_amazon_arrigo = CR_portal_amazon_arrigo
            
        CR_portal_cnova_kes = tudo['CR_portal_cnova_kes']
        if CR_portal_cnova_kes != corre.CR_portal_cnova_kes:
            corre.CR_portal_cnova_kes = CR_portal_cnova_kes
            
        CR_portal_cnova_arrigo = tudo['CR_portal_cnova_arrigo']
        if CR_portal_cnova_arrigo != corre.CR_portal_cnova_arrigo:
            corre.CR_portal_cnova_arrigo = CR_portal_cnova_arrigo
            
        CR_portal_leroy_kes = tudo['CR_portal_leroy_kes']
        if CR_portal_leroy_kes != corre.CR_portal_leroy_kes:
            corre.CR_portal_leroy_kes = CR_portal_leroy_kes
            
        CR_portal_mobly_kc = tudo['CR_portal_mobly_kc']
        if CR_portal_mobly_kc != corre.CR_portal_mobly_kc:
            corre.CR_portal_mobly_kc = CR_portal_mobly_kc
            
        CR_portal_shopee_kes = tudo['CR_portal_shopee_kes']
        if CR_portal_shopee_kes != corre.CR_portal_shopee_kes:
            corre.CR_portal_shopee_kes = CR_portal_shopee_kes
            
        CR_portal_aliexpress_arrigo = tudo['CR_portal_aliexpress_arrigo']
        if CR_portal_aliexpress_arrigo != corre.CR_portal_aliexpress_arrigo:
            corre.CR_portal_aliexpress_arrigo = CR_portal_aliexpress_arrigo
            
        CR_portal_elo7_arrigo = tudo['CR_portal_elo7_arrigo']
        if CR_portal_elo7_arrigo != corre.CR_portal_elo7_arrigo:
            corre.CR_portal_elo7_arrigo = CR_portal_elo7_arrigo
        
        if corre.CR_portal_ML_alaok == True or corre.CR_portal_ML_alaok == "True":
            if corre.CR_portal_ML_gea == True or corre.CR_portal_ML_gea == "True":
                if corre.CR_portal_ML_kes == True or corre.CR_portal_ML_kes == "True":
                    if corre.CR_portal_ML_arrigo == True or corre.CR_portal_ML_arrigo == "True":
                        if corre.CR_portal_Magalu_gea == True or corre.CR_portal_Magalu_gea == "True":
                            if corre.CR_portal_Magalu_kes == True or corre.CR_portal_Magalu_kes == "True":
                                if corre.CR_portal_Magalu_kc == True or corre.CR_portal_Magalu_kc == "True":
                                    if corre.CR_portal_Magalu_arrigo == True or corre.CR_portal_Magalu_arrigo == "True":
                                        if corre.CR_portal_carrefour_alaok == True or corre.CR_portal_carrefour_alaok == "True":
                                            if corre.CR_portal_carrefour_gea == True or corre.CR_portal_carrefour_gea == "True":
                                                if corre.CR_portal_carrefour_arrigo == True or corre.CR_portal_carrefour_arrigo == "True":
                                                    if corre.CR_portal_netshoes_alk == True or corre.CR_portal_netshoes_alk == "True":
                                                        if corre.CR_portal_netshoes_kes == True or corre.CR_portal_netshoes_kes == "True":
                                                            if corre.CR_portal_olist_gea == True or corre.CR_portal_olist_gea == "True":
                                                                if corre.CR_portal_olist_arrigo == True or corre.CR_portal_olist_arrigo == "True":
                                                                    if corre.CR_portal_madeiramadeira_kes == True or corre.CR_portal_madeiramadeira_kes == "True":
                                                                        if corre.CR_portal_madeiramadeira_arrigo == True or corre.CR_portal_madeiramadeira_arrigo == "True":
                                                                            if corre.CR_portal_amazon_kes == True or corre.CR_portal_amazon_kes == "True":
                                                                                if corre.CR_portal_amazon_kc == True or corre.CR_portal_amazon_kc == "True":
                                                                                    if corre.CR_portal_amazon_arrigo == True or corre.CR_portal_amazon_arrigo == "True":
                                                                                        if corre.CR_portal_cnova_kes == True or corre.CR_portal_cnova_kes == "True":
                                                                                            if corre.CR_portal_cnova_arrigo == True or corre.CR_portal_cnova_arrigo == "True":
                                                                                                if corre.CR_portal_leroy_kes == True or corre.CR_portal_leroy_kes == "True":
                                                                                                    if corre.CR_portal_mobly_kc == True or corre.CR_portal_mobly_kc == "True":
                                                                                                        if corre.CR_portal_shopee_kes == True or corre.CR_portal_shopee_kes == "True":
                                                                                                            if corre.CR_portal_aliexpress_arrigo == True or corre.CR_portal_aliexpress_arrigo == "True":
                                                                                                                if corre.CR_portal_elo7_arrigo == True or corre.CR_portal_elo7_arrigo == "True":
                                                                                                                    print(corre.CR_status)
                                                                                                                    corre.CR_status = "Concluido"

        corre.save()
        corre = Correcoes.objects.filter(CR_status="Andamento").order_by('CR_sku')
    else:
        corre = Correcoes.objects.filter(CR_status="Andamento").order_by('CR_sku')
    return render(request,"produto/correcoes.html",{"correcoes":corre})


@login_required
def novacorrecao(request):
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)
        sku = str(tudo['CR_sku']).upper()
        prod = Produto.objects.get(Pro_Sku = str(sku))

        prioridade = tudo['CR_prioridade']
        motivo_correcao = tudo['CR_motivo_correcao']
        links = tudo['CR_links']

        create = Correcoes.objects.create(CR_sku=sku,CR_produto=prod,CR_prioridade=prioridade,CR_motivo_correcao=motivo_correcao,CR_links=links,CR_status="Andamento",CR_portal_ML_alaok = False, CR_portal_ML_gea = False, CR_portal_ML_kes = False, CR_portal_ML_arrigo = False, CR_portal_Magalu_gea = False, CR_portal_Magalu_kes = False, CR_portal_Magalu_kc = False, CR_portal_Magalu_arrigo = False, CR_portal_b2w_alaok = False, CR_portal_b2w_kc = False, CR_portal_b2w_jcma = False, CR_portal_carrefour_alaok = False, CR_portal_carrefour_gea = False, CR_portal_carrefour_arrigo = False, CR_portal_netshoes_alk = False, CR_portal_netshoes_kes = False, CR_portal_centauro_alaok = False, CR_portal_olist_gea = False, CR_portal_olist_arrigo = False, CR_portal_leroy_kes = False, CR_portal_madeiramadeira_kes = False, CR_portal_madeiramadeira_arrigo = False, CR_portal_amazon_kes = False, CR_portal_amazon_kc = False, CR_portal_amazon_arrigo = False, CR_portal_cnova_kes = False, CR_portal_cnova_arrigo = False, CR_portal_shopee_kes = False, CR_portal_aliexpress_arrigo = False, CR_portal_mobly_kc = False, CR_portal_elo7_arrigo = False,CR_portal_Master=False)

        corre = Correcoes.objects.filter(CR_status="Andamento").order_by('CR_prioridade')    
        return render(request,"produto/correcoes.html",{"correcoes":corre})
    else:
        corre = Correcoes.objects.filter(CR_status="Andamento").order_by('CR_prioridade')    
        return render(request,"produto/novacorrecao.html",{"correcoes":corre})