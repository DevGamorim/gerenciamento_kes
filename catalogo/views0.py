#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
#Import Models
from sincronizador.models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view
from produtos.models import Produto, Preco_Portal, Confere_Preco_log, Nota
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
def conferencia(request):
    user = request.user
    produto = {}
    retorno = []
    prods = Produto.objects.filter(Pro_Conferencia_loja=True)

    if request.method == 'POST':
        if len(prods) <= 0:
            return render(request,'home.html')
        else:
            for n in range(0,len(prods)):
            
                skuh = str(prods[n].Pro_Sku)            
                link = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "1.jpg"
                produto['Pro_Sku'] = skuh
                produto['link'] = link
                produto['Pro_Nome'] = prods[n].Pro_Nome
                produto['Pro_Loja'] = prods[n].Pro_Loja
                produto['Pro_PrecoVenda'] = prods[n].Pro_PrecoVenda
                produto['updated_at'] = prods[n].updated_at
                retorno.append(dict(produto))

                data_e_hora_atuais = datetime.now()
                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                name = skuh + ' | '+str(data_e_hora_em_texto)

                obj_prod = Produto.objects.get(Pro_Sku = skuh)
                obj_prod.Pro_Conferencia_loja = False
                obj_prod.save()

                conferencia = Confere_Preco_log.objects.create(CP_nome = name,CP_Data_atualizacao = str(data_e_hora_em_texto), CP_Sku = obj_prod, CP_User = str(user), CP_preco = prods[n].Pro_PrecoVenda).save()

            return render(request,'loja/pos_conferenica.html',{'lista_skus':retorno})
    else:
        if len(prods) <= 0:
            return render(request,'loja/loja_sem.html')
        else:
                
            for n in range(0,len(prods)):
                skuh = str(prods[n].Pro_Sku)            
                link = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "1.jpg"
                produto['Pro_Sku'] = skuh
                produto['link'] = link
                produto['Pro_Nome'] = prods[n].Pro_Nome
                produto['Pro_Loja'] = prods[n].Pro_Loja
                produto['Pro_PrecoVenda'] = prods[n].Pro_PrecoVenda
                produto['updated_at'] = prods[n].updated_at
                retorno.append(dict(produto))
        return render(request,'loja/loja_conferenica.html',{'lista_skus':retorno})