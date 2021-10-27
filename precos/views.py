#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.http import HttpResponse ,JsonResponse
#Import Models
from sincronizador.models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view
from produtos.models import Produto, Preco_Portal, Confere_Preco_log, Produto_Precificacao, Fornecedores, Nota, Kit
from vendas.models import Venda
from .models import Preco_Faixa, Comissoes
from background_task.models import Task
#Import for apps
from background_task import background
import requests
import json
import yaml
from datetime import datetime, date
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
import datetime

import pyrebase
import yaml

config = {
    'apiKey': "AIzaSyBc_es9P1nML862S1D6p4mS4S0EjfZvFhI",
    'authDomain': "arrigo-pedidos.firebaseapp.com",
    'databaseURL': "https://arrigo-pedidos-default-rtdb.firebaseio.com",
    'projectId': "arrigo-pedidos",
    'storageBucket': "arrigo-pedidos.appspot.com",
    'messagingSenderId': "252620383994",
    'appId': "1:252620383994:web:b1f2b869cbdd995c4f8b43",
    'measurementId': "G-V3TMNWZZWR"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
db = firebase.database()

def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote

#@login_required
@method_decorator(login_required, name='dispatch')
class HomePageView(TemplateView):
    template_name = 'home.html'



def remove_repetidos(lista):
    l = []
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
    return l


@login_required
def todosprecos(request):
    if request.method == 'POST':
        #escolhas = request.POST.copy()
        #print(escolhas)
        escolha_skus = str(request.POST.get('skus')).upper()
        if len(escolha_skus) >= 1:
            escolha_skus = escolha_skus.replace("\n",",")
            escolha_skus = escolha_skus.replace("\t",",")
            escolha_skus = escolha_skus.replace(" ",",")
            escolha_skus = escolha_skus.split(",")
            print(escolha_skus)
            print(len(escolha_skus))
        else:
            escolha_skus = ''
        escolha_estoque = request.POST.get('estoque')

        escolha_fornecedor = request.POST.get('fornecedor')

        escolha_data = int(request.POST.get('data'))

        escolha_kits = str(request.POST.get('kits'))

        print(escolha_kits)

        if escolha_kits == 'sim':
            for i in range(0,len(escolha_skus)):
                try:
                    kits = Kit.objects.get(KT_principal_Sku=str(escolha_skus[i]))
                    print(kits)
                except:
                    print("Passou")
                    continue
                kits = kits.KT_variacoes
                kits = kits.replace("[","")
                kits = kits.replace("]","")
                kits = kits.replace("'","")
                kits = kits.replace('"',"")
                kits = kits.replace(" ","")
                kits = kits.split(",")
                escolha_skus = escolha_skus + kits
                escolha_skus = remove_repetidos(escolha_skus)

                print(escolha_skus)


        data1 = datetime.date.today()
        data2 = datetime.date.today() - datetime.timedelta(days=escolha_data)


        produto = {}
        lista_prods = []
        lista = []
        lista_def = {}
        lista_master = {}
        retorno = []
        precos=''
    # ----------------- Obter Dados de Vendas -----------------

        if escolha_data == 0:
            lista_def = {'0':0}
        else:
            vendas = Venda.objects.filter(VE_DataVenda__gte=data2, VE_DataVenda__lte=data1)
            for n in range(0,len(vendas)):
                prods_vendidos = vendas[n].VE_Itens
                for y in range(0,len(prods_vendidos)):
                    prods = prods_vendidos[y]
                    referencia = prods['ProdutoCodigo']
                    quantidade = int(str(prods['Quantidade']).replace('.00',""))
                    produto['id_master'] = referencia
                    produto['vendidos'] = quantidade
                    lista_prods.append(dict(produto))
                    lista.append(referencia)
                    
            lista = remove_repetidos(lista)
            lista_prods.sort(key=lambda x: x['id_master'], reverse=False)
            lista.sort()
            n = 0
            for n in range(0,len(lista)):
                lista_def[str(lista[n])] = 0


            n = 0
            for n in range(0,len(lista_prods)):
                ids = lista_prods[n]['id_master']
                quantidade = lista_prods[n]['vendidos']

                quant_ant = lista_def[str(ids)]
                quant_ant = quant_ant + quantidade

                lista_def[str(ids)] = quant_ant
            
    # ----------------- Obter Dados de produtos -----------------
        if len(escolha_skus) >= 1:
            for n in range(0,len(escolha_skus)):
                sku = escolha_skus[n]
                prods = Produto.objects.get(Pro_Sku=sku)

                ids = prods.Pro_Id
                print(ids)
                try:
                    precos = Produto_Precificacao.objects.get(PP_ID=ids)
                    if precos.PP_custo_adm_site == None:
                        comissoes = get_object_or_404(Comissoes, pk='1')
                        precos.PP_custo_adm_site = comissoes.CS_Custo_Adm_site
                        precos.save()
                except:
                    continue
                n = 0
                if escolha_data != 0:
                    lista_keys = list(lista_def.keys())
                    for m in range(0,len(lista_keys)):
                        
                        if str(precos.PP_ID) == lista_keys[m] or precos.PP_ID == lista_keys[m]:
                            lista_master['N_Vendas'] = lista_def[str(precos.PP_ID)]
                            break
                        else:
                            lista_master['N_Vendas'] = 0
                
                else:
                    lista_master['N_Vendas'] = "Não calculado"

                lista_master['PP_nome'] = precos.PP_nome
                lista_master['PP_ID'] = precos.PP_ID
                lista_master['PP_sku'] = precos.PP_sku
                lista_master['PP_estoque_fisico'] = precos.PP_estoque_fisico
                lista_master['PP_fornecedor'] = str(precos.PP_fornecedor).replace('A - ','')
                lista_master['PP_custo'] = precos.PP_custo
                
                try:
                    Faixa_Site = str(precos.PP_Faixa_Site)
                    lista_master['PP_Faixa_Site'] = str(Faixa_Site)+"%"
                except:
                    lista_master['PP_Faixa_Site'] =precos.PP_Faixa_Site
                try:
                    Faixa_Portal = str(precos.PP_Faixa_Portal)
                    lista_master['PP_Faixa_Portal'] = str(Faixa_Portal)+"%"
                except:
                    lista_master['PP_Faixa_Portal'] = precos[n].PP_Faixa_Portal

                custo_adm = str(precos.PP_custo_adm_site)
                custo_adm = custo_adm.replace('0.',"")
                custo_adm = custo_adm.replace('.0',"")
                lista_master['PP_custo_adm'] = str(custo_adm)+"%"

                imposto = str(precos.PP_imposto)
                imposto = imposto.replace('0.',"")
                imposto = imposto.replace('.0',"")
                lista_master['PP_imposto'] = str(imposto)+"%"

                Lucratividade_site = str(precos.PP_comissao_site)
                Lucratividade_site = Lucratividade_site.replace('0.',"")
                Lucratividade_site = Lucratividade_site.replace('.0',"")
                lista_master['PP_Lucratividade_site'] = str(Lucratividade_site)+"%"

                lista_master['Preco_venda_atual'] = "R$ "+str(prods.Pro_PrecoVenda)
                

                retorno.append(dict(lista_master))

            retorno = sorted(retorno, key=lambda k: k['N_Vendas'], reverse=True) 

            forn = Fornecedores.objects.all().order_by('FN_Nome')
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            return render(request, 'precos/todosprecos.html',{'precos':retorno,'fornecedores':forn})

        else:
            if escolha_fornecedor == "Todos":
                if escolha_estoque == "com":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__gte= 1)
                elif escolha_estoque == "sem":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__lte= 0)
                else:
                    precos = Produto_Precificacao.objects.all()
            else:
                if escolha_estoque == "com":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__gte= 1,PP_fornecedor= str(escolha_fornecedor))
                elif escolha_estoque == "sem":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__lte= 0,PP_fornecedor= str(escolha_fornecedor))
                else:
                    precos = Produto_Precificacao.objects.filter(PP_fornecedor=str(escolha_fornecedor))

            precos.PP_custo_adm_site = comissoes.CS_Custo_Adm_site
            precos.save()
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            n = 0
            print(len(precos))
            lista_keys = list(lista_def.keys())
            for n in range(0,len(precos)):
                m = 0
                for m in range(0,len(lista_keys)):
                    
                    if str(precos[n].PP_ID) == lista_keys[m] or precos[n].PP_ID == lista_keys[m]:
                        lista_master['N_Vendas'] = lista_def[str(precos[n].PP_ID)]
                        break
                    else:
                        lista_master['N_Vendas'] = 0

                prods = Produto.objects.get(Pro_Id = precos[n].PP_ID)

                lista_master['PP_nome'] = precos[n].PP_nome
                lista_master['PP_ID'] = precos[n].PP_ID
                lista_master['PP_sku'] = precos[n].PP_sku
                lista_master['PP_estoque_fisico'] = precos[n].PP_estoque_fisico
                lista_master['PP_fornecedor'] = str(precos[n].PP_fornecedor).replace('A - ','')
                lista_master['PP_custo'] = precos[n].PP_custo
                
                try:
                    Faixa_Site = str(precos[n].PP_Faixa_Site)
                    lista_master['PP_Faixa_Site'] = str(Faixa_Site)+"%"
                except:
                    lista_master['PP_Faixa_Site'] =precos[n].PP_Faixa_Site
                try:
                    Faixa_Portal = str(precos[n].PP_Faixa_Portal)
                    Faixa_Portal = str(Faixa_Portal).replace('.0',"")
                    Faixa_Portal = str(Faixa_Portal).replace('0.',"")
                    lista_master['PP_Faixa_Portal'] = str(Faixa_Portal)+"%"
                except:
                    lista_master['PP_Faixa_Portal'] = precos[n].PP_Faixa_Portal

                custo_adm = str(precos[n].PP_custo_adm_site)
                custo_adm = custo_adm.replace('0.',"")
                custo_adm = custo_adm.replace('.0',"")
                lista_master['PP_custo_adm'] = str(custo_adm)+"%"

                imposto = str(precos[n].PP_imposto)
                imposto = imposto.replace('0.',"")
                imposto = imposto.replace('.0',"")
                lista_master['PP_imposto'] = str(imposto)+"%"

                Lucratividade_site = str(precos[n].PP_comissao_site)
                Lucratividade_site = Lucratividade_site.replace('0.',"")
                Lucratividade_site = Lucratividade_site.replace('.0',"")
                lista_master['PP_Lucratividade_site'] = str(Lucratividade_site)+"%"

                lista_master['Preco_venda_atual'] = "R$ "+str(prods.Pro_PrecoVenda)
                

                retorno.append(dict(lista_master))

            retorno = sorted(retorno, key=lambda k: k['N_Vendas'], reverse=True)
            forn = Fornecedores.objects.all().order_by('FN_Nome')
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            return render(request, 'precos/todosprecos.html',{'precos':retorno,'fornecedores':forn})
    
   
    else:
        forn = Fornecedores.objects.all().order_by('FN_Nome')
        return render(request, 'precos/todosprecos.html',{'fornecedores':forn})


@login_required
def verpreco(request, id):
    preco = get_object_or_404(Produto_Precificacao, pk=id)
    comissoes = get_object_or_404(Comissoes, pk='1')
    preco_calculado = {}
# -------- amazon --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Amazon_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Amazon_KES)/100

    print("custo",custo,"\ncomiss",comiss,"\nimposto",imposto,"\ncusto_adm",custo_adm,"\nlucratividade",lucratividade)

    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    print(resul_precopor)
    preco_calculado['amazon'] = resul_precopor
# -------- B2W_ALK --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_B2W_ALK_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_B2W_ALK)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['B2W_ALK'] = resul_precopor
# -------- B2W_GEA --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_B2W_GEA_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_B2W_GEA)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['B2W_GEA'] = resul_precopor
# -------- B2W_JCMA --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_B2W_JCMA_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_B2W_JCMA)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['B2W_JCMA'] = resul_precopor
# -------- B2W_KC --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_B2W_KC_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_B2W_KC)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['B2W_KC'] = resul_precopor
# -------- Carrefour_ALK --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Carrefour_ALK_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Carrefour_ALK)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Carrefour_ALK'] = resul_precopor
# -------- Carrefour_GEA --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Carrefour_GEA_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Carrefour_GEA)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Carrefour_GEA'] = resul_precopor
# -------- Centauro_ALK --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Centauro_ALK_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Centauro_ALK)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Centauro_ALK'] = resul_precopor
# -------- Cnova_KES --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Cnova_KES_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Cnova_KES)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Cnova_KES'] = resul_precopor
# -------- MadeiraMadeira_KES --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_MM_KES_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_MadeiraMadeira_KES)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['MadeiraMadeira_KES'] = resul_precopor
# -------- Magalu_GEA --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Magalu_GEA_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Magalu_GEA)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Magalu_GEA'] = resul_precopor
# -------- Magalu_KC --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Magalu_KC_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Magalu_KC)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Magalu_KC'] = resul_precopor
# -------- Netshoes_KES --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Netshoes_KES_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Netshoes_KES)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Netshoes_KES'] = resul_precopor
# -------- Netshoes_ALK --------
    custo = float(preco.PP_custo)
    comiss = float(comissoes.CS_Netshoes_ALK_Comissao)/100
    imposto = float(preco.PP_imposto)/100
    custo_adm = float(preco.PP_custo_adm_portal)/100
    lucratividade = float(preco.PP_Netshoes_ALK)/100
    
    somaPorc = imposto + comiss + custo_adm + lucratividade
    resul_precopor = round(custo/(1-somaPorc))
    resul_precopor = float(resul_precopor) + 0.99
    preco_calculado['Netshoes_ALK'] = resul_precopor


    return render(request, 'precos/verpreco.html',{'preco':preco,"comissoes":comissoes,'calculado':preco_calculado})


@login_required
def verpreco_portais(request):
    from datetime import datetime
    if request.method == 'POST':
        id_master = request.POST.get('id')
        portal = request.POST.get('portal')
        portal_novo = str(request.POST.get('portal_novo')).replace(",",".")
        portal_antigo = str(request.POST.get('portal_antigo')).replace(",",".")
        print("portal_novo",portal_novo,'portal_antigo',portal_antigo)
        custo_adm = request.POST.get('adm')
        imposto_geral = request.POST.get('imposto_geral')
        final = request.POST.get('final')

        try:
            if final == "None" or final == None:
                final = ""
        except:
            final = ""

        try:
            portal_antigo = float(portal_antigo)
        except:
            portal_antigo = 0

        try:
            lucratividade = float(portal_novo)
        except:
            try:
                portal_novo = portal_antigo
                lucratividade = float(portal_novo)
            except:
                lucratividade = 0.0

        name_portal = portal
        preco = get_object_or_404(Produto_Precificacao, pk=id_master)
        comissoes = get_object_or_404(Comissoes, pk='1')

        print(final,len(final))

        if len(final) <= 0:
            custo = float(preco.PP_custo)
            if portal == "Amazon":
                comiss = float(comissoes.CS_Amazon_Comissao)/100
            elif portal == "B2W_ALK":
                comiss = float(comissoes.CS_B2W_ALK_Comissao)/100
            elif portal == "B2W_GEA":
                comiss = float(comissoes.CS_B2W_GEA_Comissao)/100
            elif portal == "B2W_JCMA":
                comiss = float(comissoes.CS_B2W_JCMA_Comissao)/100
            elif portal == "B2W_KC":
                comiss = float(comissoes.CS_B2W_KC_Comissao)/100
            elif portal == "Carrefour_ALK":
                comiss = float(comissoes.CS_Carrefour_ALK_Comissao)/100
            elif portal == "Carrefour_GEA":
                comiss = float(comissoes.CS_Carrefour_GEA_Comissao)/100
            elif portal == "Centauro_ALK":
                comiss = float(comissoes.CS_Centauro_ALK_Comissao)/100
            elif portal == "Cnova_KES":
                comiss = float(comissoes.CS_Cnova_KES_Comissao)/100
            elif portal == "MadeiraMadeira_KES":
                comiss = float(comissoes.CS_MM_KES_Comissao)/100
            elif portal == "Magalu_GEA":
                comiss = float(comissoes.CS_Magalu_GEA_Comissao)/100
            elif portal == "Magalu_KC":
                comiss = float(comissoes.CS_Magalu_KC_Comissao)/100
            elif portal == "Netshoes_KES":
                comiss = float(comissoes.CS_Netshoes_KES_Comissao)/100
            elif portal == "Netshoes_ALK":
                comiss = float(comissoes.CS_Netshoes_ALK_Comissao)/100


            imposto = float(preco.PP_imposto)/100
            custo_adm = float(preco.PP_custo_adm_portal)/100
            lucratividade = lucratividade/100

            print("custo",custo,"\ncomiss",comiss,"\nimposto",imposto,"\ncusto_adm",custo_adm,"\nlucratividade",lucratividade)

            somaPorc = imposto + comiss + custo_adm + lucratividade
            resul_precopor = round(custo/(1-somaPorc))
            resul_precopor = float(resul_precopor) + 0.99
            print(resul_precopor)

            

            success = [resul_precopor,id_master,"calculado"]

        else:
            custo = float(preco.PP_custo)
            if portal == "Amazon":
                comiss = float(comissoes.CS_Amazon_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Amazon_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Amazon_KES_absoluta = True
                    preco.PP_Amazon_KES = float(portal_novo)
                    preco.save()

            elif portal == "B2W_ALK":
                comiss = float(comissoes.CS_B2W_ALK_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_B2W_ALK_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_B2W_ALK_absoluta = True
                    preco.PP_B2W_ALK = float(portal_novo)
                    preco.save()

            elif portal == "B2W_GEA":
                comiss = float(comissoes.CS_B2W_GEA_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_B2W_GEA_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_B2W_GEA_absoluta = True
                    preco.PP_B2W_GEA = float(portal_novo)
                    preco.save()
                    
            elif portal == "B2W_JCMA":
                comiss = float(comissoes.CS_B2W_JCMA_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_B2W_JCMA_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_B2W_JCMA_absoluta = True
                    preco.PP_B2W_JCMA = float(portal_novo)
                    preco.save()
                    
            elif portal == "B2W_KC":
                comiss = float(comissoes.CS_B2W_KC_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_B2W_KC_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_B2W_KC_absoluta = True
                    preco.PP_B2W_KC = float(portal_novo)
                    preco.save()
                    
            elif portal == "Carrefour_ALK":
                comiss = float(comissoes.CS_Carrefour_ALK_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Carrefour_ALK_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Carrefour_ALK_absoluta = True
                    preco.PP_Carrefour_ALK = float(portal_novo)
                    preco.save()
                    
            elif portal == "Carrefour_GEA":
                comiss = float(comissoes.CS_Carrefour_GEA_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Carrefour_GEA_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Carrefour_GEA_absoluta = True
                    preco.PP_Carrefour_GEA = float(portal_novo)
                    preco.save()
                    
            elif portal == "Centauro_ALK":
                comiss = float(comissoes.CS_Centauro_ALK_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Centauro_ALK_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Centauro_ALK_absoluta = True
                    preco.PP_Centauro_ALK = float(portal_novo)
                    preco.save()
                    
            elif portal == "Cnova_KES":
                comiss = float(comissoes.CS_Cnova_KES_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Cnova_KES_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Cnova_KES_absoluta = True
                    preco.PP_Cnova_KES = float(portal_novo)
                    preco.save()
                    
            elif portal == "MadeiraMadeira_KES":
                comiss = float(comissoes.CS_MM_KES_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_MM_KES_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_MadeiraMadeira_KES_absoluta = True
                    preco.PP_MadeiraMadeira_KES = float(portal_novo)
                    preco.save()
                    
            elif portal == "Magalu_GEA":
                comiss = float(comissoes.CS_Magalu_GEA_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Magalu_GEA_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Magalu_GEA_absoluta = True
                    preco.PP_Magalu_GEA = float(portal_novo)
                    preco.save()
                    
            elif portal == "Magalu_KC":
                comiss = float(comissoes.CS_Magalu_KC_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Magalu_KC_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Magalu_KC_absoluta = True
                    preco.PP_Magalu_KC = float(portal_novo)
                    preco.save()
                    
            elif portal == "Netshoes_KES":
                comiss = float(comissoes.CS_Netshoes_KES_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Netshoes_KES_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Netshoes_KES_absoluta = True
                    preco.PP_Netshoes_KES = float(portal_novo)
                    preco.save()
                    
            elif portal == "Netshoes_ALK":
                comiss = float(comissoes.CS_Netshoes_ALK_Comissao)/100
                ID_catalogo_portal = int(comissoes.CS_Netshoes_ALK_ID)
                if float(portal_novo) != float(portal_antigo):
                    preco.PP_Netshoes_ALK_absoluta = True
                    preco.PP_Netshoes_ALK = float(portal_novo)
                    preco.save()

            imposto = float(preco.PP_imposto)/100
            custo_adm = float(preco.PP_custo_adm_portal)/100

            lucratividade = lucratividade/100

            print("custo",custo,"\ncomiss",comiss,"\nimposto",imposto,"\ncusto_adm",custo_adm,"\nlucratividade",lucratividade)

            somaPorc = imposto + comiss + custo_adm + lucratividade
            resul_precopor = round(custo/(1-somaPorc))
            resul_precopor = float(resul_precopor) + 0.99

            if resul_precopor < 0 and resul_precopor > 349.99:
                vari_por = 0.15
            elif resul_precopor < 350 and resul_precopor > 949.99:
                vari_por = 0.12
            elif resul_precopor < 950 and resul_precopor > 1999.99:
                vari_por = 0.1
            else:
                vari_por = 0.08

            resul_precode = resul_precopor*vari_por
            resul_precode = resul_precode + resul_precopor
            resul_precode = round(resul_precode)
            resul_precode = float(resul_precode + 0.99)

            Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
            headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
            ip = str(Master.SC_ip) #Ip ou link da api

            url = "http://"+str(ip)+":2082/root/produto/"+str(id_master)+"/fila"
            response = requests.request("POST", url, headers=headers)

            success = [resul_precopor,id_master,"salvo"]
            
            prodss = Produto.objects.get(Pro_Id = id_master)
            data_e_hora_atuais = datetime.now()
            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
            name = 'Atualização Preço | '+str(prodss.Pro_Sku)+' | '+str(data_e_hora_em_texto)
            
            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = str(request.user), SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = portal, SL_PrecoDe = resul_precode, SL_PrecoPor = resul_precopor, SL_Estoque = 0)

        return JsonResponse(success,safe=False)


@login_required
def alterar_faixa(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        site_novo = request.POST.get('site_novo')
        site_antigo = str(request.POST.get('site_antigo')).replace("%","")
        portal_novo = request.POST.get('portal_novo')
        portal_antigo = request.POST.get('portal_antigo')
        valor_final = request.POST.get('valor_final')
        custo = request.POST.get('custo')



        if len(site_novo) == 0:
            site_novo = float(site_antigo)

        if len(valor_final) <= 0:
            #prod = Produto.objects.get(Pro_Id = id)
            precos = get_object_or_404(Produto_Precificacao, pk=id)
            print(precos.PP_imposto)
            imposto = float(precos.PP_imposto)/100
            comissao_portal = float(precos.PP_comissao_site)/100
            CustoAdmin = float(precos.PP_custo_adm_site)/100
            classificacao = float(site_novo)/100
            print(precos.PP_custo)
            custo = str(custo).replace(",",".")
            custo = float(custo)
            
            print("imposto",imposto,'\n',"comissao_portal",comissao_portal,'\n',"CustoAdmin",CustoAdmin,'\n',"classificacao",classificacao,'\n',"custo",custo,'\n',)


            somaPorc = imposto + comissao_portal + CustoAdmin + classificacao
            resul_precopor = round(custo/(1-somaPorc))
            resul_precopor = float(resul_precopor) + 0.90
            desconto = resul_precopor*0.15
            desconto = resul_precopor - desconto
            desconto = round(desconto,2)
            desconto = "R$ "+str(desconto).replace(".9",".90")

            resul_precopor = str(resul_precopor).replace(".9",".90")
            resul_precopor = "R$ "+resul_precopor


            success = [resul_precopor,id,"calculado",desconto]

        else:   
            
            #prod = Produto.objects.get(Pro_Id = id)
            precos = get_object_or_404(Produto_Precificacao, pk=id)
            if float(site_novo) != float(site_antigo):
                precos.PP_Faixa_Site_absoluta = True
                precos.PP_Faixa_Site = site_novo
                precos.save()

            print(precos.PP_imposto)
            imposto = float(precos.PP_imposto)/100
            comissao_portal = float(precos.PP_comissao_site)/100
            CustoAdmin = float(precos.PP_custo_adm_site)/100
            classificacao = float(site_novo)/100
            custo = str(custo).replace(",",".")
            custo = float(custo)
            
            print("imposto",imposto,'\n',"comissao_portal",comissao_portal,'\n',"CustoAdmin",CustoAdmin,'\n',"classificacao",classificacao,'\n',"custo",custo,'\n',)


            somaPorc = imposto + comissao_portal + CustoAdmin + classificacao
            resul_precopor = round(custo/(1-somaPorc))
            resul_precopor = float(resul_precopor) + 0.90


            if resul_precopor < 0 and resul_precopor > 349.99:
                vari_por = 0.15
            elif resul_precopor < 350 and resul_precopor > 949.99:
                vari_por = 0.12
            elif resul_precopor < 950 and resul_precopor > 1999.99:
                vari_por = 0.1
            else:
                vari_por = 0.08

            vari_por = 0.20

            resul_precode = resul_precopor*vari_por
            resul_precode = resul_precode + resul_precopor

            resul_precode = round(resul_precode)
            resul_precode = float(resul_precode + 0.90)



            Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
            headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
            ip = str(Master.SC_ip) #Ip ou link da api

            url = "http://"+str(ip)+":2082/root/Preco/"+str(id)
            response = requests.request("GET", url, headers=headers)
            response = response.text.encode('utf8')    
            preco = json.loads(response)

            preco = preco['preco'][0]
            preco['PrecoCusto'] = preco['PrecoCusto']
            preco['PrecoVenda'] = str(resul_precopor)+'0'
            preco['PrecoFicticio'] = str(resul_precode)+'0'
            preco['PrecoSite'] = str(resul_precopor)+'0'
            preco['PrecoFicticioSite'] = str(resul_precode)+'0'
            for y in range(0,len(preco['PrecoFilhos'])):
                preco['PrecoFilhos'][y]['PrecoVenda'] = str(resul_precopor)+'0'
                preco['PrecoFilhos'][y]['PrecoFicticio'] = str(resul_precode)+'0'
                preco['PrecoFilhos'][y]['PrecoSite'] = str(resul_precopor)+'0'
                preco['PrecoFilhos'][y]['PrecoFicticioSite'] = str(resul_precode)+'0'

            print('------------------------------------')
            print(resul_precode,resul_precopor)
            print('------------------------------------')

            try:
                url = "http://"+str(ip)+":2082/root/Preco/"+str(id)
                response = requests.request("PUT", url, headers=headers, data=json.dumps(preco))
                response = response.text.encode('utf8')
                print(response)
                url = "http://"+str(ip)+":2082/root/produto/"+str(id)+"/fila"
                response = requests.request("POST", url, headers=headers, data=json.dumps(preco))
                response = response.text.encode('utf8')
                print('Salvo custos e preço! Adicionando as filas de integração!')

                prodss = Produto.objects.get(Pro_Id = id)
                data_e_hora_atuais = datetime.now()
                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                name = 'Atualização Preço | '+str(prodss.Pro_Sku)+' | '+str(data_e_hora_em_texto)
                
                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = str(request.user), SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Master", SL_PrecoDe = resul_precode, SL_PrecoPor = resul_precopor, SL_Estoque = 0)

            except:
                print('Erro ao salvar custos e preço!')

        
            resul_precopor = str(resul_precopor).replace(".9",".90")
            resul_precopor = "R$ "+ resul_precopor
            success = [resul_precopor,id,"salvo"]
        print(success)
        return JsonResponse(success,safe=False)


#Se precisar subir algo em massa
@login_required
def importar(request):
    from datetime import datetime
    Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
    headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
    ip = str(Master.SC_ip) #Ip ou link da api
    if request.method == 'POST':
        ids = str(request.POST.get('ids')).upper()
        if len(ids) >= 1:
            ids = ids.replace("\n",",")
            ids = ids.replace("\t",",")
            ids = ids.replace(" ",",")
            ids = ids.split(",")
            print(ids)
            print(len(ids))
        else:
            ids = ''

        for n in range(0,len(ids)):
            url = "http://"+ip+":2082/root/produto/"+str(ids[n])

            response = requests.request("GET", url, headers=headers)
            response = response.text.encode('utf8')
            response = json.loads(response)
            produtos = response['produto']
            print()
            estoqueloja = 0   
            estoquebarracao = 0
            vetor = produtos[0]
            sku = vetor['Referencia']
            if sku == 'INATIVO':
                url = "http://"+ip+":2082/root/produto/" + str(vetor['Codigo']) + "/ok"
                response = requests.request("POST", url, headers=headers)
                continue

            url = "http://"+ip+":2082/root/estoque/"+str(vetor['Codigo'])
            response = requests.request("GET", url, headers=headers)
            response = response.text.encode('utf8')
            estoque = json.loads(response)
            estoque = estoque['estoque']
            estoque = estoque[0]
            try:
                estoque = estoque['MultiEstoque']
                for nn in range(0,len(estoque)):
                    vetor2 = estoque[nn]
                    local = vetor2['Localizacao']
                    local = local['Nome']
                    if local == 'LOJA':
                        estoqueloja = float(vetor2['Saldo'])
                        estoqueloja = int(estoqueloja)
                    elif local == 'BARRACÃO':
                        estoquebarracao = float(vetor2['Saldo'])
                        estoquebarracao = int(estoquebarracao)
            except:
                estoquebarracao = float(estoque['EstoqueSite'])
                estoquebarracao = int(estoquebarracao)

            url = "http://"+ip+":2082/root/estoque/" + str(vetor['Codigo']) + "/ok"
            response = requests.request("POST", url, headers=headers)

            estoqueatual = float(vetor['EstoqueAtual'])
            estoqueatual = int(estoqueatual)

            EstoqueMaximo = float(vetor['EstoqueMaximo'])
            EstoqueMaximo = int(EstoqueMaximo)

            QuantidadeTerceiros = float(vetor['QuantidadeTerceiros'])
            QuantidadeTerceiros = int(QuantidadeTerceiros)

            if vetor['Referencia'] == '':
                nome = vetor['Codigo']
            else:
                nome = vetor['Referencia']

            data_e_hora_atuais = datetime.now()
            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')

            name = 'Master Produto | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)

            try:
                if estoqueloja >= 1:
                    prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                    sku = prodss.Pro_Sku
                    if sku[:2] != 'KT':
                        if prodss.Pro_PrecoVenda != vetor['PrecoVenda']:
                            mudanca_preco = True
                        else:
                            mudanca_preco = False
                    else:
                        mudanca_preco = False
                elif estoqueloja <= 0:
                    mudanca_preco = False
                else:
                    mudanca_preco = False

            except:
                mudanca_preco = False

            try:
                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                prodss.Pro_Sku = str(nome)
                prodss.Pro_Conferencia_loja = mudanca_preco
                prodss.Pro_Nome = vetor['Nome']
                prodss.Pro_EstoqueBarracao = estoquebarracao
                prodss.Pro_Loja = estoqueloja
                prodss.Pro_EstoqueTotal = estoqueatual
                prodss.Pro_Ean = vetor['EAN']
                prodss.Pro_Ativo = vetor['Ativo']
                prodss.Pro_LocalizacaoSetor = vetor['LocalizacaoSetor']
                prodss.Pro_LocalizacaoBox = vetor['LocalizacaoBox']
                prodss.Pro_SemEan = vetor['SubstituirEANPorSemGTIN']
                prodss.Pro_FornecedorCodigo = vetor['FornecedorCodigo']
                prodss.Pro_FabricanteCodigo = vetor['FabricanteCodigo']
                prodss.Pro_Classificacao = vetor['Classificacao']
                prodss.Pro_Modelo = vetor['Modelo']
                prodss.Pro_Conteudo = vetor['Conteudo']
                prodss.Pro_DescricaoCurta = vetor['DescricaoCurta']
                prodss.Pro_DescricaoLonga = vetor['DescricaoLonga']
                prodss.Pro_PrecoCusto = vetor['PrecoCusto']
                prodss.Pro_PrecoVenda = vetor['PrecoVenda']
                prodss.Pro_PrecoFicticio = str(vetor['PrecoFicticioSite'])
                prodss.Pro_Altura = vetor['Altura']
                prodss.Pro_Largura = vetor['Largura']
                prodss.Pro_Profundidade = vetor['Profundidade']
                prodss.Pro_Peso = vetor['Peso']
                prodss.Pro_NCM = vetor['NCM']
                prodss.Pro_Composicao = vetor['Composicao']
                prodss.Pro_CategoriaPrincipal = vetor['CategoriaPrincipal']
                prodss.Pro_DisponibilidadeEmEstoque = vetor['DisponibilidadeEmEstoque']
                prodss.Pro_DisponibilidadeSemEstoque = vetor['DisponibilidadeSemEstoque']
                prodss.Pro_PromocaoInicio = vetor['PromocaoInicio']
                prodss.Pro_PromocaoFim = vetor['PromocaoFim']
                prodss.Pro_PrevalecerPrecoPai = vetor['PrevalecerPrecoPai']
                prodss.Pro_Taxa = vetor['Taxa']
                prodss.Pro_NumeroMaximoParcelas = vetor['NumeroMaximoParcelas']
                prodss.Pro_EstoqueMaximo = EstoqueMaximo
                prodss.Pro_TipoDisponibilidade = vetor['TipoDisponibilidade']
                prodss.Pro_PreVenda = vetor['PreVenda']
                prodss.Pro_PreVendaData = vetor['PreVendaData']
                prodss.Pro_PreVendaLimite = vetor['PreVendaLimite']
                prodss.Pro_VendaSemEstoque = vetor['VendaSemEstoque']
                prodss.Pro_VendaSemEstoqueData = vetor['VendaSemEstoqueData']
                prodss.Pro_VendaSemEstoqueLimite = vetor['VendaSemEstoqueLimite']
                prodss.Pro_ExibirDisponibilidade = vetor['ExibirDisponibilidade']
                prodss.Pro_TipoReposicao = vetor['TipoReposicao']
                prodss.Pro_PesoCubico = vetor['PesoCubico']
                prodss.Pro_QuantidadeMaximaPorCliente = vetor['QuantidadeMaximaPorCliente']
                prodss.Pro_FreteGratis = vetor['FreteGratis']
                prodss.Pro_TituloVariacao = vetor['TituloVariacao']
                prodss.Pro_TituloSubVariacao = vetor['TituloSubVariacao']
                prodss.Pro_MetaTitle = vetor['MetaTitle']
                prodss.Pro_MetaDescription = vetor['MetaDescription']
                prodss.Pro_MetaKeywords = vetor['MetaKeywords']
                prodss.Pro_PalavrasParaPesquisa = vetor['PalavrasParaPesquisa']
                prodss.Pro_Ordem = vetor['Ordem']
                prodss.Pro_VisualizarUrlDireto = vetor['VisualizarUrlDireto']
                prodss.Pro_TemOpcaoPresente = vetor['TemOpcaoPresente']
                prodss.Pro_PresenteValor = float(vetor['PresenteValor'])
                prodss.Pro_Video = vetor['Video']
                prodss.Pro_UnidadeSigla = vetor['UnidadeSigla']
                prodss.Pro_Foto = vetor['Foto']
                prodss.Pro_ControlaEstoque = vetor['ControlaEstoque']
                prodss.Pro_Fornecedores = vetor['Fornecedores']
                prodss.Pro_Imagens = vetor['Imagens']
                prodss.Pro_CodigoPai = vetor['CodigoPai']
                prodss.Pro_EstoqueSite = vetor['EstoqueSite']
                prodss.Pro_Composto = vetor['Composto']
                prodss.Pro_Grade = vetor['Grade']
                prodss.Pro_QuantidadeTerceiros = QuantidadeTerceiros
                prodss.Pro_CST = vetor['CST']
                prodss.Pro_NomeAbreviado = vetor['NomeAbreviado']
                prodss.Pro_IPICST = vetor['IPICST']
                prodss.Pro_PISCST = vetor['PISCST']
                prodss.Pro_COFINSCST = vetor['COFINSCST']
                prodss.Pro_PISAliquota = float(vetor['PISAliquota'])
                prodss.Pro_COFINSAliquota = float(vetor['COFINSAliquota'])
                prodss.Pro_CFOPCodigo = vetor['CFOPCodigo']
                prodss.Pro_ICMSTipo = vetor['ICMSTipo']
                prodss.Pro_ICMSST = float(vetor['ICMSST'])
                prodss.Pro_CSTOrigem = vetor['CSTOrigem']
                prodss.Pro_PrecoFicticioSite = vetor['PrecoFicticioSite']
                prodss.Pro_PrecoSite = vetor['PrecoSite']
                prodss.Pro_ICMSVenda = float(vetor['ICMSVenda'])
                prodss.Pro_Volume = vetor['Volume']
                prodss.Pro_ItensInclusos = vetor['ItensInclusos']
                prodss.Pro_DadosTecnicos = vetor['DadosTecnicos']
                prodss.Pro_Categorias = vetor['Categorias']
                prodss.Pro_Unidade = vetor['Unidade']
                prodss.Pro_Thumbnail = vetor['Thumbnail']
                prodss.Pro_EnviarSite = vetor['EnviarSite']
                prodss.Pro_Comissao = vetor['Comissao']
                prodss.Pro_ExibeEsgotado = vetor['ExibeEsgotado']
                prodss.Pro_CSOSN = vetor['CSOSN']
                prodss.Pro_CEST = vetor['CEST']
                prodss.Pro_ICMSCompraAliquota = vetor['ICMSCompraAliquota']
                prodss.Pro_ICMSSTBase = vetor['ICMSSTBase']
                prodss.Pro_ICMSReducaoBaseCalculo = vetor['ICMSReducaoBaseCalculo']
                prodss.Pro_ICMSBase = vetor['ICMSBase']
                prodss.Pro_IPIAliquota = vetor['IPIAliquota']
                prodss.Pro_IPICompraAliquota = vetor['IPICompraAliquota']
                prodss.Pro_ISSAliquota = vetor['ISSAliquota']
                prodss.Pro_ISSCSERV = vetor['ISSCSERV']
                prodss.Pro_Lista = vetor['Lista']
                prodss.Pro_GrupoTributacao = vetor['GrupoTributacao']
                prodss.Pro_DefinicaoPrecoEscopo = vetor['DefinicaoPrecoEscopo']
                prodss.Pro_VtexLojasId = vetor['VtexLojasId']
                prodss.Pro_DefinicaoProdutoCodigo = vetor['DefinicaoProdutoCodigo']
                prodss.Pro_Slug = vetor['Slug']
                prodss.Pro_AtrelamentoDescricao = vetor['AtrelamentoDescricao']
                prodss.Pro_BeneficiosDescricao = vetor['BeneficiosDescricao']
                prodss.Pro_DestaqueDescricao = vetor['DestaqueDescricao']
                prodss.Pro_PromocaoDescricao = vetor['PromocaoDescricao']
                prodss.Pro_GanheBrindeDescricao = vetor['GanheBrindeDescricao']
                prodss.Pro_LancamentoDescricao = vetor['LancamentoDescricao']
                prodss.Pro_MedidasDescricao = vetor['MedidasDescricao']
                prodss.Pro_QuemUsaDescricao = vetor['QuemUsaDescricao']
                prodss.Pro_SeguroDescricao = vetor['SeguroDescricao']
                prodss.Pro_SugestaoDeUsoDescricao = vetor['SugestaoDeUsoDescricao']
                prodss.Pro_PercentualMarkupPrecoMargem = vetor['PercentualMarkupPrecoMargem']
                prodss.Pro_PrecoPercentual = vetor['PrecoPercentual']
                prodss.Pro_PrevalecerPromoPai = vetor['PrevalecerPromoPai']
                prodss.Pro_PontosFidelidade = vetor['PontosFidelidade']
                prodss.Pro_SemEntregas = vetor['SemEntregas']
                prodss.Pro_ExibirNovo = vetor['ExibirNovo']
                prodss.Pro_ExibirNovoInicio = vetor['ExibirNovoInicio']
                prodss.Pro_ExibirNovoFim = vetor['ExibirNovoFim']
                prodss.Pro_EstoqueMinimoIndisponibilizar = vetor['EstoqueMinimoIndisponibilizar']
                prodss.Pro_EstoqueMinimoNotificar = vetor['EstoqueMinimoNotificar']
                prodss.Pro_ExibirProdutoInicio = vetor['ExibirProdutoInicio']
                prodss.Pro_ExibirProdutoFim = vetor['ExibirProdutoFim']
                prodss.Pro_CoreExibirPreco = vetor['CoreExibirPreco']
                prodss.Pro_BundleOpcao = vetor['BundleOpcao']
                prodss.Pro_Flag = vetor['Flag']
                prodss.Pro_Acabamento = vetor['Acabamento']
                prodss.Pro_AnoPublicacao = vetor['AnoPublicacao']
                prodss.Pro_Assunto = vetor['Assunto']
                prodss.Pro_Autor = vetor['Autor']
                prodss.Pro_Colecao = vetor['Colecao']
                prodss.Pro_Edicao = vetor['Edicao']
                prodss.Pro_Editora = vetor['Editora']
                prodss.Pro_Formato = vetor['Formato']
                prodss.Pro_Idioma = vetor['Idioma']
                prodss.Pro_ISBN = vetor['ISBN']
                prodss.Pro_ISBN13 = vetor['ISBN13']
                prodss.Pro_Pagina = vetor['Pagina']
                prodss.Pro_Titulo = vetor['Titulo']
                prodss.Pro_Tradutor = vetor['Tradutor']
                prodss.Pro_CamposRelacionaveis = vetor['CamposRelacionaveis']
                prodss.Pro_Editor = vetor['Editor']
                prodss.Pro_Ilustrador = vetor['Ilustrador']
                prodss.Pro_Organizador = vetor['Organizador']
                prodss.Pro_Fotografo = vetor['Fotografo']
                prodss.Pro_PaisOrigem = vetor['PaisOrigem']
                prodss.Pro_DataPublicacao = vetor['DataPublicacao']
                prodss.Pro_NVolume = vetor['NVolume']
                prodss.Pro_EditaSinopse = vetor['EditaSinopse']
                prodss.Pro_BarraExtra = vetor['BarraExtra']
                prodss.save()
                print(n,vetor['Referencia'],'Importado Update no banco!')	
                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                sinc = Sinc_log.objects.create(SL_Nome = name, SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoVenda'], SL_PrecoPor = vetor['PrecoFicticioSite'], SL_Estoque = 0)


            except Produto.DoesNotExist:
                Produto(Pro_Id = vetor['Codigo'], Pro_Sku = str(nome), Pro_Nome = vetor['Nome'], Pro_EstoqueBarracao = estoquebarracao, Pro_Loja = estoqueloja, Pro_EstoqueTotal = estoqueatual, Pro_Ean = vetor['EAN'], Pro_Ativo = vetor['Ativo'], Pro_LocalizacaoSetor = vetor['LocalizacaoSetor'], Pro_LocalizacaoBox = vetor['LocalizacaoBox'], Pro_SemEan = vetor['SubstituirEANPorSemGTIN'], Pro_FornecedorCodigo = vetor['FornecedorCodigo'], Pro_FabricanteCodigo = vetor['FabricanteCodigo'], Pro_Classificacao = vetor['Classificacao'], Pro_Modelo = vetor['Modelo'], Pro_Conteudo = vetor['Conteudo'], Pro_DescricaoCurta = vetor['DescricaoCurta'], Pro_DescricaoLonga = vetor['DescricaoLonga'], Pro_PrecoCusto = vetor['PrecoCusto'], Pro_PrecoVenda = vetor['PrecoVenda'], Pro_PrecoFicticio = str(vetor['PrecoFicticioSite']), Pro_Altura = vetor['Altura'], Pro_Largura = vetor['Largura'], Pro_Profundidade = vetor['Profundidade'], Pro_Peso = vetor['Peso'], Pro_NCM = vetor['NCM'], Pro_Composicao = vetor['Composicao'], Pro_CategoriaPrincipal = vetor['CategoriaPrincipal'], Pro_DisponibilidadeEmEstoque = vetor['DisponibilidadeEmEstoque'], Pro_DisponibilidadeSemEstoque = vetor['DisponibilidadeSemEstoque'], Pro_PromocaoInicio = vetor['PromocaoInicio'], Pro_PromocaoFim = vetor['PromocaoFim'], Pro_PrevalecerPrecoPai = vetor['PrevalecerPrecoPai'], Pro_Taxa = vetor['Taxa'], Pro_NumeroMaximoParcelas = vetor['NumeroMaximoParcelas'], Pro_EstoqueMaximo = EstoqueMaximo, Pro_TipoDisponibilidade = vetor['TipoDisponibilidade'], Pro_PreVenda = vetor['PreVenda'], Pro_PreVendaData = vetor['PreVendaData'], Pro_PreVendaLimite = vetor['PreVendaLimite'], Pro_VendaSemEstoque = vetor['VendaSemEstoque'], Pro_VendaSemEstoqueData = vetor['VendaSemEstoqueData'], Pro_VendaSemEstoqueLimite = vetor['VendaSemEstoqueLimite'], Pro_ExibirDisponibilidade = vetor['ExibirDisponibilidade'], Pro_TipoReposicao = vetor['TipoReposicao'], Pro_PesoCubico = vetor['PesoCubico'], Pro_QuantidadeMaximaPorCliente = vetor['QuantidadeMaximaPorCliente'], Pro_FreteGratis = vetor['FreteGratis'], Pro_TituloVariacao = vetor['TituloVariacao'], Pro_TituloSubVariacao = vetor['TituloSubVariacao'], Pro_MetaTitle = vetor['MetaTitle'], Pro_MetaDescription = vetor['MetaDescription'], Pro_MetaKeywords = vetor['MetaKeywords'], Pro_PalavrasParaPesquisa = vetor['PalavrasParaPesquisa'], Pro_Ordem = vetor['Ordem'], Pro_VisualizarUrlDireto = vetor['VisualizarUrlDireto'], Pro_TemOpcaoPresente = vetor['TemOpcaoPresente'], Pro_PresenteValor = float(vetor['PresenteValor']), Pro_Video = vetor['Video'], Pro_UnidadeSigla = vetor['UnidadeSigla'], Pro_Foto = vetor['Foto'], Pro_ControlaEstoque = vetor['ControlaEstoque'], Pro_Fornecedores = vetor['Fornecedores'], Pro_Imagens = vetor['Imagens'], Pro_CodigoPai = vetor['CodigoPai'], Pro_EstoqueSite = vetor['EstoqueSite'], Pro_Composto = vetor['Composto'], Pro_Grade = vetor['Grade'], Pro_QuantidadeTerceiros = QuantidadeTerceiros, Pro_CST = vetor['CST'], Pro_NomeAbreviado = vetor['NomeAbreviado'], Pro_IPICST = vetor['IPICST'], Pro_PISCST = vetor['PISCST'], Pro_COFINSCST = vetor['COFINSCST'], Pro_PISAliquota = float(vetor['PISAliquota']), Pro_COFINSAliquota = float(vetor['COFINSAliquota']), Pro_CFOPCodigo = vetor['CFOPCodigo'], Pro_ICMSTipo = vetor['ICMSTipo'], Pro_ICMSST = float(vetor['ICMSST']), Pro_CSTOrigem = vetor['CSTOrigem'], Pro_PrecoFicticioSite = vetor['PrecoFicticioSite'], Pro_PrecoSite = vetor['PrecoSite'], Pro_ICMSVenda = float(vetor['ICMSVenda']), Pro_Volume = vetor['Volume'], Pro_ItensInclusos = vetor['ItensInclusos'], Pro_DadosTecnicos = vetor['DadosTecnicos'], Pro_Categorias = vetor['Categorias'], Pro_Unidade = vetor['Unidade'], Pro_Thumbnail = vetor['Thumbnail'], Pro_EnviarSite = vetor['EnviarSite'], Pro_Comissao = vetor['Comissao'], Pro_ExibeEsgotado = vetor['ExibeEsgotado'], Pro_CSOSN = vetor['CSOSN'], Pro_CEST = vetor['CEST'], Pro_ICMSCompraAliquota = vetor['ICMSCompraAliquota'], Pro_ICMSSTBase = vetor['ICMSSTBase'], Pro_ICMSReducaoBaseCalculo = vetor['ICMSReducaoBaseCalculo'], Pro_ICMSBase = vetor['ICMSBase'], Pro_IPIAliquota = vetor['IPIAliquota'], Pro_IPICompraAliquota = vetor['IPICompraAliquota'], Pro_ISSAliquota = vetor['ISSAliquota'], Pro_ISSCSERV = vetor['ISSCSERV'], Pro_Lista = vetor['Lista'], Pro_GrupoTributacao = vetor['GrupoTributacao'], Pro_DefinicaoPrecoEscopo = vetor['DefinicaoPrecoEscopo'], Pro_VtexLojasId = vetor['VtexLojasId'], Pro_DefinicaoProdutoCodigo = vetor['DefinicaoProdutoCodigo'], Pro_Slug = vetor['Slug'], Pro_AtrelamentoDescricao = vetor['AtrelamentoDescricao'], Pro_BeneficiosDescricao = vetor['BeneficiosDescricao'], Pro_DestaqueDescricao = vetor['DestaqueDescricao'], Pro_PromocaoDescricao = vetor['PromocaoDescricao'], Pro_GanheBrindeDescricao = vetor['GanheBrindeDescricao'], Pro_LancamentoDescricao = vetor['LancamentoDescricao'], Pro_MedidasDescricao = vetor['MedidasDescricao'], Pro_QuemUsaDescricao = vetor['QuemUsaDescricao'], Pro_SeguroDescricao = vetor['SeguroDescricao'], Pro_SugestaoDeUsoDescricao = vetor['SugestaoDeUsoDescricao'], Pro_PercentualMarkupPrecoMargem = vetor['PercentualMarkupPrecoMargem'], Pro_PrecoPercentual = vetor['PrecoPercentual'], Pro_PrevalecerPromoPai = vetor['PrevalecerPromoPai'], Pro_PontosFidelidade = vetor['PontosFidelidade'], Pro_SemEntregas = vetor['SemEntregas'], Pro_ExibirNovo = vetor['ExibirNovo'], Pro_ExibirNovoInicio = vetor['ExibirNovoInicio'], Pro_ExibirNovoFim = vetor['ExibirNovoFim'], Pro_EstoqueMinimoIndisponibilizar = vetor['EstoqueMinimoIndisponibilizar'], Pro_EstoqueMinimoNotificar = vetor['EstoqueMinimoNotificar'], Pro_ExibirProdutoInicio = vetor['ExibirProdutoInicio'], Pro_ExibirProdutoFim = vetor['ExibirProdutoFim'], Pro_CoreExibirPreco = vetor['CoreExibirPreco'], Pro_BundleOpcao = vetor['BundleOpcao'], Pro_Flag = vetor['Flag'], Pro_Acabamento = vetor['Acabamento'], Pro_AnoPublicacao = vetor['AnoPublicacao'], Pro_Assunto = vetor['Assunto'], Pro_Autor = vetor['Autor'], Pro_Colecao = vetor['Colecao'], Pro_Edicao = vetor['Edicao'], Pro_Editora = vetor['Editora'], Pro_Formato = vetor['Formato'], Pro_Idioma = vetor['Idioma'], Pro_ISBN = vetor['ISBN'], Pro_ISBN13 = vetor['ISBN13'], Pro_Pagina = vetor['Pagina'], Pro_Titulo = vetor['Titulo'], Pro_Tradutor = vetor['Tradutor'], Pro_CamposRelacionaveis = vetor['CamposRelacionaveis'], Pro_Editor = vetor['Editor'], Pro_Ilustrador = vetor['Ilustrador'], Pro_Organizador = vetor['Organizador'], Pro_Fotografo = vetor['Fotografo'], Pro_PaisOrigem = vetor['PaisOrigem'], Pro_DataPublicacao = vetor['DataPublicacao'], Pro_NVolume = vetor['NVolume'], Pro_EditaSinopse = vetor['EditaSinopse'], Pro_BarraExtra = vetor['BarraExtra']).save()
                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                sinc = Sinc_log.objects.create(SL_Nome = name, SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoFicticioSite'], SL_PrecoPor = vetor['PrecoVenda'], SL_Estoque = 0)
                print(n,vetor['Referencia'],'Importado Cadastrado no banco!')

            if vetor['FabricanteCodigo'] == 916 or vetor['FabricanteCodigo'] == '916':
                data = {}
                data['SKU'] = vetor['Referencia']
                data['ID_master'] = vetor['Codigo']
                data['Titulo'] = vetor['Nome']
                data['Preco_tabela'] = vetor['PrecoVenda']		

                db.child("Produtos").child(vetor['Referencia']).set(data)
                print(vetor['Referencia'],'arrigo')

            custo = vetor['PrecoCusto']
            custo = custo.replace('"','')
            custo = custo.replace("'","")
            custo = float(custo)

            try:
                comiss = get_object_or_404(Comissoes, pk='1')
                PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))
                PRO_LUC.PP_custo = custo
                PRO_LUC.PP_nome = vetor['Nome']
                try:
                    prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])                
                    fornecedor = prodss.Pro_Fornecedores
                    fornecedor = json.dumps(fornecedor)
                    fornecedor = json.loads(fornecedor)                
                    fornecedor = fornecedor[0]
                    fornecedor = fornecedor['FornecedorCodigo']
                    forn = Fornecedores.objects.get(FN_ID = fornecedor)
                    fornecedor = forn.FN_Nome
                except:
                    fornecedor = 'Não informado'

                #print(fornecedor)
                PRO_LUC.PP_fornecedor = fornecedor

                if PRO_LUC.PP_Classificao_total_absoluta != True:

                    if PRO_LUC.PP_comissao_site_absoluta != True:
                        PRO_LUC.PP_comissao_site = comiss.CS_Comissao_site
                    
                    if PRO_LUC.PP_Amazon_KES_absoluta != True:
                        PRO_LUC.PP_Amazon_KES = comiss.CS_Amazon_Comissao
                    
                    if PRO_LUC.PP_B2W_ALK_absoluta != True:
                        PRO_LUC.PP_B2W_ALK = comiss.CS_B2W_ALK_Comissao

                    if PRO_LUC.PP_B2W_GEA_absoluta != True:
                        PRO_LUC.PP_B2W_GEA = comiss.CS_B2W_GEA_Comissao                                

                    if PRO_LUC.PP_B2W_JCMA_absoluta != True:
                        PRO_LUC.PP_B2W_JCMA = comiss.CS_B2W_JCMA_Comissao

                    if PRO_LUC.PP_B2W_KC_absoluta != True:
                        PRO_LUC.PP_B2W_KC = comiss.CS_B2W_KC_Comissao

                    if PRO_LUC.PP_Carrefour_ALK_absoluta != True:
                        PRO_LUC.PP_Carrefour_ALK = comiss.CS_Carrefour_ALK_Comissao

                    if PRO_LUC.PP_Carrefour_GEA_absoluta != True:
                        PRO_LUC.PP_Carrefour_GEA = comiss.CS_Carrefour_GEA_Comissao

                    if PRO_LUC.PP_Centauro_ALK_absoluta != True:
                        PRO_LUC.PP_Centauro_ALK = comiss.CS_Centauro_ALK_Comissao

                    if PRO_LUC.PP_Cnova_KES_absoluta != True:
                        PRO_LUC.PP_Cnova_KES = comiss.CS_Cnova_KES_Comissao

                    if PRO_LUC.PP_MadeiraMadeira_KES_absoluta != True:
                        PRO_LUC.PP_MadeiraMadeira_KES = comiss.CS_MM_KES_Comissao

                    if PRO_LUC.PP_Magalu_GEA_absoluta != True:
                        PRO_LUC.PP_Magalu_GEA = comiss.CS_Magalu_GEA_Comissao

                    if PRO_LUC.PP_Magalu_KC_absoluta != True:
                        PRO_LUC.PP_Magalu_KC = comiss.CS_Magalu_KC_Comissao
                    
                    if PRO_LUC.PP_Netshoes_KES_absoluta != True:
                        PRO_LUC.PP_Netshoes_KES = comiss.CS_Netshoes_KES_Comissao
                    
                    if PRO_LUC.PP_Netshoes_ALK_absoluta != True:
                        PRO_LUC.PP_Netshoes_ALK = comiss.CS_Netshoes_ALK_Comissao
                    
                    Master_LocalizacaoSetor = vetor['LocalizacaoSetor']
                    Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace('"','')
                    Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace("'","")

                    if PRO_LUC.PP_Faixa_Portal_absoluta != True:

                        if Master_LocalizacaoSetor == "A":
                            try:
                                precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                                a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                                
                                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)
                                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                                maior_3000 = float(precofaixa.PF_maior_3000)
                                print("A")
                            except:
                                a0_a_4_99 = 30
                                a5_a_14_99 = 28
                                a15_a_29_99 = 15                             
                                a30_a_49_99 = 0
                                a50_a_79_99 = 0
                                a80_a_119_99 = 0
                                a120_a_149_99 = 0
                                a150_a_199_99 = 0
                                a200_a_249_99 = 0
                                a250_a_299_99 = 0
                                a300_a_349_99 = 0
                                a350_a_399_99 = 0
                                a400_a_449_99 = 0
                                a450_a_549_99 = 0
                                a550_a_649_99 = 0
                                a650_a_749_99 = 0
                                a750_a_899_99 = 0
                                a900_a_999_99 = 0
                                a1000_a_1499_99 = 0
                                a1500_a_1999_99 = 0
                                a2000_a_2499_99 = 0
                                a2500_a_2999_99 = 0
                                maior_3000 = 0
                                print("A Padrão")
                        elif Master_LocalizacaoSetor == 'B':
                            try:
                                precofaixa = Preco_Faixa.objects.get(PF_ID = '6')
                                a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)
                                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                                
                                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                                maior_3000 = float(precofaixa.PF_maior_3000)

                                print("B")
                            except:
                                a0_a_4_99 = 40
                                a5_a_14_99 = 35
                                a15_a_29_99 = 25                             
                                a30_a_49_99 = 20
                                a50_a_79_99 = 15
                                a80_a_119_99 = 13
                                a120_a_149_99 = 11
                                a150_a_199_99 = 10
                                a200_a_249_99 = 9
                                a250_a_299_99 = 8
                                a300_a_349_99 = 7.5
                                a350_a_399_99 = 7
                                a400_a_449_99 = 6.5
                                a450_a_549_99 = 6
                                a550_a_649_99 = 5.5
                                a650_a_749_99 = 5
                                a750_a_899_99 = 4.5
                                a900_a_999_99 = 4
                                a1000_a_1499_99 = 3.5
                                a1500_a_1999_99 = 3
                                a2000_a_2499_99 = 3
                                a2500_a_2999_99 = 3
                                maior_3000 = 3
                                print("B Padrão")
                        else:
                            a0_a_4_99 = 40
                            a5_a_14_99 = 35
                            a15_a_29_99 = 25                             
                            a30_a_49_99 = 20
                            a50_a_79_99 = 15
                            a80_a_119_99 = 13
                            a120_a_149_99 = 11
                            a150_a_199_99 = 10
                            a200_a_249_99 = 9
                            a250_a_299_99 = 8
                            a300_a_349_99 = 7.5
                            a350_a_399_99 = 7
                            a400_a_449_99 = 6.5
                            a450_a_549_99 = 6
                            a550_a_649_99 = 5.5
                            a650_a_749_99 = 5
                            a750_a_899_99 = 4.5
                            a900_a_999_99 = 4
                            a1000_a_1499_99 = 35
                            a1500_a_1999_99 = 3
                            a2000_a_2499_99 = 3
                            a2500_a_2999_99 = 3
                            maior_3000 = 3
                            print("Sem classificação")

                        if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                            if custo <= 4.99:
                                classificacao = a0_a_4_99

                            elif custo >= 5 and custo <= 14.99:
                                classificacao = a5_a_14_99

                            elif custo >= 15 and custo <= 29.99:
                                classificacao = a15_a_29_99

                            elif custo >= 30 and custo <= 49.99:
                                classificacao = a30_a_49_99

                            elif custo >= 50 and custo <= 79.99:
                                classificacao = a50_a_79_99

                            elif custo >= 80 and custo <= 119.99:
                                classificacao = a80_a_119_99

                            elif custo >= 120 and custo <= 149.99:
                                classificacao = a120_a_149_99

                            elif custo >= 150 and custo <= 199.99:
                                classificacao = a150_a_199_99

                            elif custo >= 200 and custo <= 249.99:
                                classificacao = a200_a_249_99
                                
                            elif custo >= 250 and custo <= 299.99:
                                classificacao = a250_a_299_99

                            elif custo >= 300 and custo <= 349.99:
                                classificacao = a300_a_349_99

                            elif custo >= 350 and custo <= 399.99:
                                classificacao = a350_a_399_99

                            elif custo >= 400 and custo <= 449.99:
                                classificacao = a400_a_449_99

                            elif custo >= 450 and custo <= 549.99:
                                classificacao = a450_a_549_99

                            elif custo >= 550 and custo <= 649.99:
                                classificacao = a550_a_649_99

                            elif custo >= 650 and custo <= 749.99:
                                classificacao = a650_a_749_99

                            elif custo >= 750 and custo <= 899.99:
                                classificacao = a750_a_899_99

                            elif custo >= 900 and custo <= 999.99:
                                classificacao = a900_a_999_99

                            elif custo >= 1000 and custo <= 1499.99:
                                classificacao = a1000_a_1499_99

                            elif custo >= 1500 and custo <= 1999.99:
                                classificacao = a1500_a_1999_99

                            elif custo >= 2000 and custo <= 2499.99:
                                classificacao = a2000_a_2499_99

                            elif custo >= 2500 and custo <= 2999.99:
                                classificacao = a2500_a_2999_99

                            elif custo >= 3000:
                                classificacao = maior_3000

                        else:
                            classificacao = '00'
                    
                        PRO_LUC.PP_Faixa_Portal = classificacao
                    
                    if PRO_LUC.PP_Faixa_Site_absoluta != True:
                        if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                            try:
                                faixa = Preco_Faixa.objects.get(PF_ID = '2')

                                a0_a_4_99 = float(faixa.PF_0_a_4_99)

                                a5_a_14_99 = float(faixa.PF_5_a_14_99)

                                a15_a_29_99 = float(faixa.PF_15_a_29_99)
                                
                                a30_a_49_99 = float(faixa.PF_30_a_49_99)

                                a50_a_79_99 = float(faixa.PF_50_a_79_99)

                                a80_a_119_99 = float(faixa.PF_80_a_119_99)

                                a120_a_149_99 = float(faixa.PF_120_a_149_99)
                                a150_a_199_99 = float(faixa.PF_150_a_199_99)

                                a200_a_249_99 = float(faixa.PF_200_a_249_99)

                                a250_a_299_99 = float(faixa.PF_250_a_299_99)

                                a300_a_349_99 = float(faixa.PF_300_a_349_99)
                                a350_a_399_99 = float(faixa.PF_350_a_399_99)
                                a400_a_449_99 = float(faixa.PF_400_a_449_99)

                                a450_a_549_99 = float(faixa.PF_450_a_549_99)

                                a550_a_649_99 = float(faixa.PF_550_a_649_99)

                                a650_a_749_99 = float(faixa.PF_650_a_749_99)

                                a750_a_899_99 = float(faixa.PF_750_a_899_99)

                                a900_a_999_99 = float(faixa.PF_900_a_999_99)

                                a1000_a_1499_99 = float(faixa.PF_1000_a_1499_99)

                                a1500_a_1999_99 = float(faixa.PF_1500_a_1999_99)

                                a2000_a_2499_99 = float(faixa.PF_2000_a_2499_99)

                                a2500_a_2999_99 = float(faixa.PF_2500_a_2999_99)

                                maior_3000 = float(faixa.PF_maior_3000)

                            except:
                                a0_a_4_99 = 30
                                a5_a_14_99 = 15
                                a15_a_29_99 = 10                                    
                                a30_a_49_99 = 8
                                a50_a_79_99 = 7
                                a80_a_119_99 = 5
                                a120_a_149_99 = 3
                                a150_a_199_99 = 3
                                a200_a_249_99 = 3
                                a250_a_299_99 = 3
                                a300_a_349_99 = 3
                                a350_a_399_99 = 3
                                a400_a_449_99 = 3
                                a450_a_549_99 = 3
                                a550_a_649_99 = 3
                                a650_a_749_99 = 3
                                a750_a_899_99 = 3
                                a900_a_999_99 = 2
                                a1000_a_1499_99 = 1
                                a1500_a_1999_99 = 1
                                a2000_a_2499_99 = 1
                                a2500_a_2999_99 = 1
                                maior_3000 = 1

                            if custo <= 4.99:
                                classificacao = a0_a_4_99

                            elif custo >= 5 and custo <= 14.99:
                                classificacao = a5_a_14_99

                            elif custo >= 15 and custo <= 29.99:
                                classificacao = a15_a_29_99

                            elif custo >= 30 and custo <= 49.99:
                                classificacao = a30_a_49_99

                            elif custo >= 50 and custo <= 79.99:
                                classificacao = a50_a_79_99

                            elif custo >= 80 and custo <= 119.99:
                                classificacao = a80_a_119_99

                            elif custo >= 120 and custo <= 149.99:
                                classificacao = a120_a_149_99

                            elif custo >= 150 and custo <= 199.99:
                                classificacao = a150_a_199_99

                            elif custo >= 200 and custo <= 249.99:
                                classificacao = a200_a_249_99
                                
                            elif custo >= 250 and custo <= 299.99:
                                classificacao = a250_a_299_99

                            elif custo >= 300 and custo <= 349.99:
                                classificacao = a300_a_349_99

                            elif custo >= 350 and custo <= 399.99:
                                classificacao = a350_a_399_99

                            elif custo >= 400 and custo <= 449.99:
                                classificacao = a400_a_449_99

                            elif custo >= 450 and custo <= 549.99:
                                classificacao = a450_a_549_99

                            elif custo >= 550 and custo <= 649.99:
                                classificacao = a550_a_649_99

                            elif custo >= 650 and custo <= 749.99:
                                classificacao = a650_a_749_99

                            elif custo >= 750 and custo <= 899.99:
                                classificacao = a750_a_899_99

                            elif custo >= 900 and custo <= 999.99:
                                classificacao = a900_a_999_99

                            elif custo >= 1000 and custo <= 1499.99:
                                classificacao = a1000_a_1499_99

                            elif custo >= 1500 and custo <= 1999.99:
                                classificacao = a1500_a_1999_99

                            elif custo >= 2000 and custo <= 2499.99:
                                classificacao = a2000_a_2499_99

                            elif custo >= 2500 and custo <= 2999.99:
                                classificacao = a2500_a_2999_99

                            elif custo >= 3000:
                                classificacao = maior_3000
                                
                        else:
                            classificacao = '00'

                        PRO_LUC.PP_Faixa_Site = classificacao


                    PRO_LUC.save()
                    #print('alterado')

            except:
                try:
                    prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])                
                    fornecedor = prodss.Pro_Fornecedores
                    fornecedor = json.dumps(fornecedor)
                    fornecedor = json.loads(fornecedor)                
                    fornecedor = fornecedor[0]
                    fornecedor = fornecedor['FornecedorCodigo']
                    forn = Fornecedores.objects.get(FN_ID = fornecedor)
                    fornecedor = forn.FN_Nome
                except:
                    fornecedor = 'Não informado'

                #print(fornecedor)
                Master_LocalizacaoSetor = vetor['LocalizacaoSetor']
                Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace('"','')
                Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace("'","")

                if Master_LocalizacaoSetor == "A":
                    try:
                        precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                        a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                        a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                        a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                        a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                        a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                        a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                        a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                        a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                        a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                        a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                        a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                        a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                        a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                        a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                        a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                        a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                        a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                        maior_3000 = float(precofaixa.PF_maior_3000)
                        print("A")
                    except:
                        a0_a_4_99 = 30
                        a5_a_14_99 = 28
                        a15_a_29_99 = 15                             
                        a30_a_49_99 = 0
                        a50_a_79_99 = 0
                        a80_a_119_99 = 0
                        a120_a_149_99 = 0
                        a150_a_199_99 = 0
                        a200_a_249_99 = 0
                        a250_a_299_99 = 0
                        a300_a_349_99 = 0
                        a350_a_399_99 = 0
                        a400_a_449_99 = 0
                        a450_a_549_99 = 0
                        a550_a_649_99 = 0
                        a650_a_749_99 = 0
                        a750_a_899_99 = 0
                        a900_a_999_99 = 0
                        a1000_a_1499_99 = 0
                        a1500_a_1999_99 = 0
                        a2000_a_2499_99 = 0
                        a2500_a_2999_99 = 0
                        maior_3000 = 0
                        print("A Padrão")
                elif Master_LocalizacaoSetor == 'B':
                    try:
                        precofaixa = Preco_Faixa.objects.get(PF_ID = '6')
                        a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                        a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                        a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                        a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                        a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                        a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                        a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                        a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                        a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                        a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                        a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                        a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                        a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                        a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                        a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                        a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                        a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                        maior_3000 = float(precofaixa.PF_maior_3000)
                        print("B")
                    except:
                        a0_a_4_99 = 40
                        a5_a_14_99 = 35
                        a15_a_29_99 = 25                             
                        a30_a_49_99 = 20
                        a50_a_79_99 = 15
                        a80_a_119_99 = 13
                        a120_a_149_99 = 11
                        a150_a_199_99 = 10
                        a200_a_249_99 = 9
                        a250_a_299_99 = 8
                        a300_a_349_99 = 7.5
                        a350_a_399_99 = 7
                        a400_a_449_99 = 6.5
                        a450_a_549_99 = 6
                        a550_a_649_99 = 5.5
                        a650_a_749_99 = 5
                        a750_a_899_99 = 4.5
                        a900_a_999_99 = 4
                        a1000_a_1499_99 = 3.5
                        a1500_a_1999_99 = 3
                        a2000_a_2499_99 = 3
                        a2500_a_2999_99 = 3
                        maior_3000 = 3
                        print("B Padrão")
                else:
                    a0_a_4_99 = 40
                    a5_a_14_99 = 35
                    a15_a_29_99 = 25                             
                    a30_a_49_99 = 20
                    a50_a_79_99 = 15
                    a80_a_119_99 = 13
                    a120_a_149_99 = 11
                    a150_a_199_99 = 10
                    a200_a_249_99 = 9
                    a250_a_299_99 = 8
                    a300_a_349_99 = 7.5
                    a350_a_399_99 = 7
                    a400_a_449_99 = 6.5
                    a450_a_549_99 = 6
                    a550_a_649_99 = 5.5
                    a650_a_749_99 = 5
                    a750_a_899_99 = 4.5
                    a900_a_999_99 = 4
                    a1000_a_1499_99 = 3.5
                    a1500_a_1999_99 = 3
                    a2000_a_2499_99 = 3
                    a2500_a_2999_99 = 3
                    maior_3000 = 3
                    print("Sem classificação")
                if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                    if custo <= 4.99:
                        classificacao = a0_a_4_99

                    elif custo >= 5 and custo <= 14.99:
                        classificacao = a5_a_14_99

                    elif custo >= 15 and custo <= 29.99:
                        classificacao = a15_a_29_99

                    elif custo >= 30 and custo <= 49.99:
                        classificacao = a30_a_49_99

                    elif custo >= 50 and custo <= 79.99:
                        classificacao = a50_a_79_99

                    elif custo >= 80 and custo <= 119.99:
                        classificacao = a80_a_119_99

                    elif custo >= 120 and custo <= 149.99:
                        classificacao = a120_a_149_99

                    elif custo >= 150 and custo <= 199.99:
                        classificacao = a150_a_199_99

                    elif custo >= 200 and custo <= 249.99:
                        classificacao = a200_a_249_99
                        
                    elif custo >= 250 and custo <= 299.99:
                        classificacao = a250_a_299_99

                    elif custo >= 300 and custo <= 349.99:
                        classificacao = a300_a_349_99

                    elif custo >= 350 and custo <= 399.99:
                        classificacao = a350_a_399_99

                    elif custo >= 400 and custo <= 449.99:
                        classificacao = a400_a_449_99

                    elif custo >= 450 and custo <= 549.99:
                        classificacao = a450_a_549_99

                    elif custo >= 550 and custo <= 649.99:
                        classificacao = a550_a_649_99

                    elif custo >= 650 and custo <= 749.99:
                        classificacao = a650_a_749_99

                    elif custo >= 750 and custo <= 899.99:
                        classificacao = a750_a_899_99

                    elif custo >= 900 and custo <= 999.99:
                        classificacao = a900_a_999_99

                    elif custo >= 1000 and custo <= 1499.99:
                        classificacao = a1000_a_1499_99

                    elif custo >= 1500 and custo <= 1999.99:
                        classificacao = a1500_a_1999_99

                    elif custo >= 2000 and custo <= 2499.99:
                        classificacao = a2000_a_2499_99

                    elif custo >= 2500 and custo <= 2999.99:
                        classificacao = a2500_a_2999_99

                    elif custo >= 3000:
                        classificacao = maior_3000
                else:
                    classificacao = '00'

                faixa_portal = classificacao

                if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                    try:
                        faixa = Preco_Faixa.objects.get(PF_ID = '2')

                        a0_a_4_99 = float(faixa.PF_0_a_4_99)

                        a5_a_14_99 = float(faixa.PF_5_a_14_99)

                        a15_a_29_99 = float(faixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(faixa.PF_30_a_49_99)

                        a50_a_79_99 = float(faixa.PF_50_a_79_99)

                        a80_a_119_99 = float(faixa.PF_80_a_119_99)

                        a120_a_149_99 = float(faixa.PF_120_a_149_99)

                        a150_a_199_99 = float(faixa.PF_150_a_199_99)

                        a200_a_249_99 = float(faixa.PF_200_a_249_99)

                        a250_a_299_99 = float(faixa.PF_250_a_299_99)

                        a300_a_349_99 = float(faixa.PF_300_a_349_99)

                        a350_a_399_99 = float(faixa.PF_350_a_399_99)

                        a400_a_449_99 = float(faixa.PF_400_a_449_99)

                        a450_a_549_99 = float(faixa.PF_450_a_549_99)

                        a550_a_649_99 = float(faixa.PF_550_a_649_99)

                        a650_a_749_99 = float(faixa.PF_650_a_749_99)

                        a750_a_899_99 = float(faixa.PF_750_a_899_99)

                        a900_a_999_99 = float(faixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(faixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(faixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(faixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(faixa.PF_2500_a_2999_99)

                        maior_3000 = float(faixa.PF_maior_3000)

                    except:
                        a0_a_4_99 = 30
                        a5_a_14_99 = 15
                        a15_a_29_99 = 10                                    
                        a30_a_49_99 = 8
                        a50_a_79_99 = 7
                        a80_a_119_99 = 5
                        a120_a_149_99 = 3
                        a150_a_199_99 = 3
                        a200_a_249_99 = 3
                        a250_a_299_99 = 3
                        a300_a_349_99 = 3
                        a350_a_399_99 = 3
                        a400_a_449_99 = 3
                        a450_a_549_99 = 3
                        a550_a_649_99 = 3
                        a650_a_749_99 = 3
                        a750_a_899_99 = 3
                        a900_a_999_99 = 2
                        a1000_a_1499_99 = 1
                        a1500_a_1999_99 = 1
                        a2000_a_2499_99 = 1
                        a2500_a_2999_99 = 1
                        maior_3000 = 1

                    if custo <= 4.99:
                        classificacao = a0_a_4_99

                    elif custo >= 5 and custo <= 14.99:
                        classificacao = a5_a_14_99

                    elif custo >= 15 and custo <= 29.99:
                        classificacao = a15_a_29_99

                    elif custo >= 30 and custo <= 49.99:
                        classificacao = a30_a_49_99

                    elif custo >= 50 and custo <= 79.99:
                        classificacao = a50_a_79_99

                    elif custo >= 80 and custo <= 119.99:
                        classificacao = a80_a_119_99

                    elif custo >= 120 and custo <= 149.99:
                        classificacao = a120_a_149_99

                    elif custo >= 150 and custo <= 199.99:
                        classificacao = a150_a_199_99

                    elif custo >= 200 and custo <= 249.99:
                        classificacao = a200_a_249_99
                        
                    elif custo >= 250 and custo <= 299.99:
                        classificacao = a250_a_299_99

                    elif custo >= 300 and custo <= 349.99:
                        classificacao = a300_a_349_99

                    elif custo >= 350 and custo <= 399.99:
                        classificacao = a350_a_399_99

                    elif custo >= 400 and custo <= 449.99:
                        classificacao = a400_a_449_99

                    elif custo >= 450 and custo <= 549.99:
                        classificacao = a450_a_549_99

                    elif custo >= 550 and custo <= 649.99:
                        classificacao = a550_a_649_99

                    elif custo >= 650 and custo <= 749.99:
                        classificacao = a650_a_749_99

                    elif custo >= 750 and custo <= 899.99:
                        classificacao = a750_a_899_99

                    elif custo >= 900 and custo <= 999.99:
                        classificacao = a900_a_999_99

                    elif custo >= 1000 and custo <= 1499.99:
                        classificacao = a1000_a_1499_99

                    elif custo >= 1500 and custo <= 1999.99:
                        classificacao = a1500_a_1999_99

                    elif custo >= 2000 and custo <= 2499.99:
                        classificacao = a2000_a_2499_99

                    elif custo >= 2500 and custo <= 2999.99:
                        classificacao = a2500_a_2999_99

                    elif custo >= 3000:
                        classificacao = maior_3000
                        
                else:
                    classificacao = '00'

                faixa_site = classificacao
                create = Produto_Precificacao.objects.create(PP_ID = int(vetor['Codigo']),PP_sku = prodss, PP_nome = str(vetor['Nome']), PP_estoque_fisico = int(estoqueatual), PP_fornecedor = str(fornecedor), PP_custo = float(custo),PP_custo_adm_site=float(comiss.CS_Custo_Adm_site), PP_custo_adm_portal = float(comiss.CS_Custo_Adm_portal), PP_imposto = float(comiss.CS_Impostos), PP_Classificao_total_absoluta = False, PP_Classificao_total = 0, PP_comissao_site_absoluta = False, PP_comissao_site = float(comiss.CS_Comissao_site), PP_Faixa_Portal = faixa_portal, PP_Faixa_Site = faixa_site,PP_Amazon_KES_absoluta = False, PP_Amazon_KES = float(comiss.CS_Amazon_Comissao), PP_B2W_ALK_absoluta = False, PP_B2W_ALK = float(comiss.CS_B2W_ALK_Comissao), PP_B2W_GEA_absoluta = False, PP_B2W_GEA = float(comiss.CS_B2W_GEA_Comissao), PP_B2W_JCMA_absoluta = False, PP_B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao), PP_B2W_KC_absoluta = False, PP_B2W_KC = float(comiss.CS_B2W_KC_Comissao), PP_Carrefour_ALK_absoluta = False, PP_Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao), PP_Carrefour_GEA_absoluta = False, PP_Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao), PP_Centauro_ALK_absoluta = False, PP_Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao), PP_Cnova_KES_absoluta = False, PP_Cnova_KES = float(comiss.CS_Cnova_KES_Comissao), PP_MadeiraMadeira_KES_absoluta = False, PP_MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao), PP_Magalu_GEA_absoluta = False, PP_Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao), PP_Magalu_KC_absoluta = False, PP_Magalu_KC = float(comiss.CS_Magalu_KC_Comissao), PP_Netshoes_KES_absoluta = False, PP_Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao), PP_Netshoes_ALK_absoluta = False, PP_Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao))
                print(vetor['Codigo'], "cadastrdo")
                #print(vetor['Codigo'], 'criado Produto_Precificacao')

        return render(request, 'precos/impostar.html',{'ids':ids})
    
    else:
        return render(request, 'precos/impostar.html')


@login_required
def enviaromni(request):
    from datetime import datetime
    usuario = request.user
    setor = request.user.Us_Setor
    if setor == "ti":
        
        preco = Produto_Precificacao.objects.all().order_by('PP_sku')
        comiss = Comissoes.objects.get(pk='1')
        for n in range(4975,len(preco)):
            PRO_LUC = preco[n] 
            skus = str(PRO_LUC.PP_sku)
            custo = float(PRO_LUC.PP_custo)
            print(n,skus,custo)
            try:           
                class_Amazon_KES = float(PRO_LUC.PP_Amazon_KES)/100
                Amazon_KES = float(comiss.CS_Amazon_Comissao)/100
                class_B2W_ALK = float(PRO_LUC.PP_B2W_ALK)/100
                B2W_ALK = float(comiss.CS_B2W_ALK_Comissao)/100
                class_B2W_GEA = float(PRO_LUC.PP_B2W_GEA)/100
                B2W_GEA = float(comiss.CS_B2W_GEA_Comissao)/100
                class_B2W_JCMA = float(PRO_LUC.PP_B2W_JCMA)/100
                B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao)/100
                class_B2W_KC = float(PRO_LUC.PP_B2W_KC)/100
                B2W_KC = float(comiss.CS_B2W_KC_Comissao)/100
                class_Carrefour_ALK = float(PRO_LUC.PP_Carrefour_ALK)/100
                Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao)/100
                class_Carrefour_GEA = float(PRO_LUC.PP_Carrefour_GEA)/100
                Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao)/100
                class_Centauro_ALK = float(PRO_LUC.PP_Centauro_ALK)/100
                Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao)/100
                class_Cnova_KES = float(PRO_LUC.PP_Cnova_KES)/100
                Cnova_KES = float(comiss.CS_Cnova_KES_Comissao)/100
                class_MadeiraMadeira_KES = float(PRO_LUC.PP_MadeiraMadeira_KES)/100
                MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao)/100
                class_Magalu_GEA = float(PRO_LUC.PP_Magalu_GEA)/100
                Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao)/100
                class_Magalu_KC = float(PRO_LUC.PP_Magalu_KC)/100
                Magalu_KC = float(comiss.CS_Magalu_KC_Comissao)/100
                class_Netshoes_KES = float(PRO_LUC.PP_Netshoes_KES)/100
                Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao)/100
                class_Netshoes_ALK = float(PRO_LUC.PP_Netshoes_ALK)/100
                Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao)/100        

                '''portais = [
                    {'nome':'Amazon-KES','comissao':Amazon_KES,'ID_catalogo':2624,'classificacao':class_Amazon_KES,},
                    {'nome':'B2W-ALK','comissao':B2W_ALK,'ID_catalogo':2780,'classificacao':class_B2W_ALK,},
                    {'nome':'B2W-GEA','comissao':B2W_GEA,'ID_catalogo':2787,'classificacao':class_B2W_GEA,},
                    {'nome':'B2W-JCMA','comissao':B2W_JCMA,'ID_catalogo':2994,'classificacao':class_B2W_JCMA,},
                    {'nome':'B2W-KC','comissao':B2W_KC,'ID_catalogo':2786,'classificacao':class_B2W_KC,},
                    {'nome':'Carrefour-ALK','comissao':Carrefour_ALK,'ID_catalogo':2640,'classificacao':class_Carrefour_ALK,},
                    {'nome':'Carrefour-GEA','comissao':Carrefour_GEA,'ID_catalogo':2918,'classificacao':class_Carrefour_GEA,},
                    {'nome':'Centauro-ALK','comissao':Centauro_ALK,'ID_catalogo':3003,'classificacao':class_Centauro_ALK,},
                    {'nome':'Cnova-KES','comissao':Cnova_KES,'ID_catalogo':2648,'classificacao':class_Cnova_KES,},
                    {'nome':'MadeiraMadeira-KES','comissao':MadeiraMadeira_KES,'ID_catalogo':2342,'classificacao':class_MadeiraMadeira_KES,},
                    {'nome':'Magalu-GEA','comissao':Magalu_GEA,'ID_catalogo':2829,'classificacao':class_Magalu_GEA,},
                    {'nome':'Magalu-KC','comissao':Magalu_KC,'ID_catalogo':2587,'classificacao':class_Magalu_KC,},
                    {'nome':'Netshoes-KES','comissao':Netshoes_KES,'ID_catalogo':2584,'classificacao':class_Netshoes_KES,},
                    {'nome':'Netshoes-ALK','comissao':Netshoes_ALK,'ID_catalogo':2440,'classificacao':class_Netshoes_ALK,}]
                '''
                portais = [{'nome':'Netshoes-ALK','comissao':Netshoes_ALK,'ID_catalogo':2440,'classificacao':class_Netshoes_ALK,}]

                imposto = float(PRO_LUC.PP_imposto)/100
                CustoAdmin = float(PRO_LUC.PP_custo_adm_portal)/100
                comissao = float(PRO_LUC.PP_comissao_site)/100

            except:
                print(n,PRO_LUC.PP_sku, "não atualizado")
                continue

        # --------------- "logar" na omni --------------- #
            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.267',
            }

            login_data = {
                'Email': '***',
                'Password': '***',
                'RememberMe': 'false',
            }

            cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

            sku = str(skus)
        # --------------- Script altereação --------------- #
            with requests.Session() as r:
                #sku = str(input('Digite o SKU: '))

                url = 'https://admin.fomnichannel.com.br/Account/Login?ReturnUrl=%2FGerenciador%2FDashboard'
                response = r.get(url, headers=headers)
                soup = BeautifulSoup(response.content, 'html5lib')
                tree = html.fromstring(response.content)
                buyers = tree.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
                __RequestVerificationToken = '__RequestVerificationToken='+str(buyers)
                headers = {
                    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.267',
                    'Referer':'https://admin.fomnichannel.com.br/Gerenciador/Produto'
                }
                login_data['__RequestVerificationToken'] = str(buyers)

                response = r.post(url, data=login_data, headers=headers)
                produtoPESQUISA = '{"' + 'Produto' + '":'+'"'+str(sku)+'"}'
                prod_data = {
                    'sEcho': '3',
                    'iColumns': '4',
                    'sColumns': '',
                    'iDisplayStart': '0',
                    'iDisplayLength': '10',
                    'mDataProp_0': '0',
                    'mDataProp_1': '1',
                    'mDataProp_2': '2',
                    'mDataProp_3': '3',
                    'sSearch': '',
                    'bRegex': 'false',
                    'sSearch_0': '',
                    'bRegex_0': 'false',
                    'bSearchable_0': 'true',
                    'sSearch_1': '',
                    'bRegex_1': 'false',
                    'bSearchable_1': 'true',
                    'sSearch_2': '',
                    'bRegex_2': 'false',
                    'bSearchable_2': 'true',
                    'sSearch_3': '',
                    'bRegex_3': 'false',
                    'bSearchable_3': 'true',
                    'iSortCol_0': '0',
                    'sSortDir_0': 'asc',
                    'iSortingCols': '1',
                    'bSortable_0': 'false',
                    'bSortable_1': 'false',
                    'bSortable_2': 'false',
                    'bSortable_3': 'false',
                    'sFiltros': str(produtoPESQUISA),
                }

                mapeamentovariante_data = {'sEcho': '2','iColumns': '9','sColumns': '','iDisplayStart': '0',
                'iDisplayLength': '50','mDataProp_0': '0','mDataProp_1': '1','mDataProp_2': '2','mDataProp_3': '3','mDataProp_4': '4','mDataProp_5': '5','mDataProp_6': '6','mDataProp_7': '7','mDataProp_8': '8','sSearch': '','bRegex': 'false','sSearch_0': '','bRegex_0': 'false','bSearchable_0': 'true','sSearch_1': '','bRegex_1': 'false','bSearchable_1': 'true','sSearch_2': '','bRegex_2': 'false','bSearchable_2': 'true','sSearch_3': '','bRegex_3': 'false','bSearchable_3': 'true','sSearch_4': '','bRegex_4': 'false','bSearchable_4': 'true','sSearch_5': '','bRegex_5': 'false','bSearchable_5': 'true','sSearch_6': '','bRegex_6': 'false','bSearchable_6': 'true','sSearch_7': '','bRegex_7': 'false','bSearchable_7': 'true','sSearch_8': '','bRegex_8': 'false','bSearchable_8': 'true'}
            # --------------- Encontrar ID produto --------------- #
                response = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/LoadGrid',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(prod_data))
                #try:
                json_prod = response.json()
                #except:
                #    print(sku,'Erro ao tentar atualizar!')
                id_prod = json_prod['aaData']
                for num in range(0,len(id_prod)):
                    textprod = id_prod[num]
                    get_produto = {
                            'produtoId':str(textprod[0]),
                        }
                    get_ = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/GetStatusProduto/',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(get_produto))
                    
                    response = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/GetStatusProduto/',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(get_produto))
                    
                    url = 'https://admin.fomnichannel.com.br/Gerenciador/Produto/LoadGridMapeamentoVariantes?produtoId=' + str(textprod[0])
                    
                    response = r.post(url,headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(mapeamentovariante_data))
                    try:
                        json_prod = response.json()
                    except:
                        continue
                    if len(json_prod['aaData']) == 0:
                        print(n,sku, 'não encontrado na omni')
                        continue                     
                    
                    else:
                        try:
                            sku_prod = json_prod['aaData']
                            sku_prod = sku_prod[0]
                            sku_prod = sku_prod[0]
                            
                        except:
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'Não encontrado Omni | '+str(skus)+' | '+str(data_e_hora_em_texto)
                            
                            prodss = Produto.objects.get(Pro_Id = PRO_LUC.PP_ID)
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)
                            continue
                try:
                    if len(sku_prod) == 0:
                        print(n,sku, 'não encontrado na omni')
                        data_e_hora_atuais = datetime.now()
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        name = 'Não encontrado Omni | '+str(skus)+' | '+str(data_e_hora_em_texto)
                        
                        prodss = Produto.objects.get(Pro_Id = PRO_LUC.PP)
                        sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)

                        continue
                except:
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                    name = 'Não encontrado Omni | '+str(skus)+' | '+str(data_e_hora_em_texto)
                    
                    prodss = Produto.objects.get(Pro_Id = PRO_LUC.PP)
                    sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)
                    print(n,name)
                    continue

                if str(sku_prod) == sku:
            
            # --------------- Calcular preço omni --------------- #
                    for cont in range(0,len(portais)):

                        info_portais = portais[cont]
                        name_portal = info_portais['nome']
                        classificacao = info_portais['classificacao']
                        comissao_portal = info_portais['comissao']
                        ID_catalogo_portal = info_portais['ID_catalogo']
                        
                        #print("imposto",imposto,'\n',"comissao_portal",comissao_portal,'\n',"CustoAdmin",CustoAdmin,'\n',"classificacao",classificacao,'\n',)
                        if CustoAdmin == None:
                            CustoAdmin = 14/100

                        somaPorc = imposto + comissao_portal + CustoAdmin + classificacao
                        resul_precopor = round(custo/(1-somaPorc))
                        resul_precopor = float(resul_precopor) + 0.99

                        if resul_precopor <= custo:
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'Aviso Preco Inferior Omni '+name_portal+' | '+str(skus)+' | '+str(data_e_hora_em_texto)
                            print(n,name_portal,'Preco de:',resul_precode,'| Preco por:',resul_precopor,'Erro')
                            prodss = Produto.objects.get(Pro_Id = PRO_LUC.PP_ID)
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(custo.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = 0)
                            continue

                        if resul_precopor < 0 and resul_precopor > 349.99:
                            vari_por = 0.15
                        elif resul_precopor < 350 and resul_precopor > 949.99:
                            vari_por = 0.12
                        elif resul_precopor < 950 and resul_precopor > 1999.99:
                            vari_por = 0.1
                        else:
                            vari_por = 0.08
                        resul_precode = resul_precopor*vari_por
                        resul_precode = resul_precode + resul_precopor
                        resul_precode = round(resul_precode)
                        resul_precode = float(resul_precode + 0.99)
            # --------------- Enviar preço Omni--------------- #

                        resul_precode = str(resul_precode)
                        resul_precode = resul_precode.replace('.',',')
                        resul_precopor = str(resul_precopor)
                        resul_precopor = resul_precopor.replace('.',',')
                        preco_data = {'produtos[]': int(textprod[0]),'canais': int(ID_catalogo_portal),'acao': 3,'tipoRegra': 6,'tipoPreco': 1,'ajuste': '','destinoPrecoDe': resul_precode,'destinoPrecoPor': resul_precopor,}
                        response = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/ExecutaAcao/',data=preco_data)
                        if response.status_code == 200:
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'Omni '+name_portal+' | '+str(skus)+' | '+str(data_e_hora_em_texto)
                            print(n,name_portal,'Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                            prodss = Produto.objects.get(Pro_Id = PRO_LUC.PP_ID)
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(resul_precode.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = 0)

                        else:
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'ERRO Omni '+name_portal+' | '+str(skus)+' | '+str(data_e_hora_em_texto)
                            print(n,'Erro ao atualizar',sku,name_portal)
                            prodss = Produto.objects.get(Pro_Id = PP_ID)
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss, SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(resul_precode.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = 0)



        return render(request, 'precos/todosprecos.html')

    else:
        return render(request, 'precos/todosprecos.html')


@login_required
def nova_nota(request):
    from datetime import datetime
    user = request.user
    forn = Fornecedores.objects.all().order_by('FN_Nome')
    if request.method == 'POST':
        numero_nf = request.POST.get('nf')
        fornecedor = request.POST.get('fornecedor')
        calcular_custo = request.POST.get('difal')            
        escolha_skus = str(request.POST.get('skus')).upper()
        if len(escolha_skus) >= 1:
            escolha_skus = escolha_skus.replace("\n",",")
            escolha_skus = escolha_skus.replace("\t",",")
            escolha_skus = escolha_skus.replace(" ",",")
            escolha_skus = escolha_skus.split(",")
        else:
            escolha_skus = ''

        for i in range(0,len(escolha_skus)):
            try:
                kits = Kit.objects.get(KT_principal_Sku=escolha_skus[i])
            except:
                continue
            kits = kits.KT_variacoes
            kits = kits.replace("[","")
            kits = kits.replace("]","")
            kits = kits.replace("'","")
            kits = kits.replace('"','')
            kits = kits.replace(" ","")
            kits = kits.split(",")
            escolha_skus = escolha_skus + kits
            escolha_skus = remove_repetidos(escolha_skus)

            print(escolha_skus)

        for n in range(0,len(escolha_skus)):
            sku = escolha_skus[n]
            if sku[:2] == "KT":
                continue
            else:
                try:
                    prod = Produto.objects.get(Pro_Sku=sku)
                except:
                    continue

                if calcular_custo == 'sim':
                    tipo_icms = str(prod.Pro_ICMSTipo)
                    proc_icms = str(prod.Pro_ICMSCompraAliquota)
                    ipi_compra = str(prod.Pro_IPICompraAliquota)
                    custo = str(prod.Pro_PrecoCusto)
                    custo = custo.replace(",",".")
                    custo = float(custo)

                    if tipo_icms == "TT" and proc_icms == "4.00":
                        ipi_compra = ipi_compra.replace(",",".")
                        ipi_compra = float(ipi_compra)/100

                        if ipi_compra == 0.45:
                            porc_ipi = 0.689655
                        elif ipi_compra == 0.40:
                            porc_ipi = 0.714286
                        elif ipi_compra == 0.35:
                            porc_ipi = 0.740741
                        elif ipi_compra == 0.20:
                            porc_ipi = 0.833334
                        elif ipi_compra == 0.18:
                            porc_ipi = 0.847458
                        elif ipi_compra == 0.15:
                            porc_ipi = 0.869565
                        elif ipi_compra == 0.12:
                            porc_ipi = 0.892857
                        elif ipi_compra == 0.10:
                            porc_ipi = 0.909091
                        elif ipi_compra == 0.08:
                            porc_ipi = 0.925926
                        elif ipi_compra == 0.05:
                            porc_ipi = 0.952381
                        elif ipi_compra == 0.0 or ipi_compra == 0:
                            porc_ipi = "+8"
                        else:
                            print("aviso Dev")
                            continue
                        if porc_ipi == "+8":
                            custo_antigo = custo
                            custo_compra = custo*0.08
                            custo = round(custo + custo_compra,2)
                            prod.Pro_PrecoCusto = custo
                        else:
                            custo_antigo = custo
                            custo_compra = round(custo*porc_ipi,2)
                            custo_compra = custo_compra*0.08
                            custo = round(custo + custo_compra,2)
                            prod.Pro_PrecoCusto = custo

                        Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
                        headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
                        ip = str(Master.SC_ip) #Ip ou link da api
                        url = "http://"+str(ip)+":2082/root/Preco/"+str(prod.Pro_Id)
                        response = requests.request("GET", url, headers=headers)
                        response = response.text.encode('utf8')    
                        preco = json.loads(response)

                        preco = preco['preco'][0]
                        preco['PrecoCusto'] = str(custo)

                        #try:
                        url = "http://"+str(ip)+":2082/root/Preco/"+str(prod.Pro_Id)
                        response = requests.request("PUT", url, headers=headers, data=json.dumps(preco))
                        response = response.text.encode('utf8')
                        print(response)
                        url = "http://"+str(ip)+":2082/root/produto/"+str(prod.Pro_Id)+"/fila"
                        response = requests.request("POST", url, headers=headers, data=json.dumps(preco))
                        response = response.text.encode('utf8')
                        print(sku,'Salvo custo ! Adicionando as filas de integração!')
                        #except:
                        #    print(sku,'Erro ao salvar custo!')

                        
                        data_e_hora_atuais = datetime.now()
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        name = 'Atualização Preço | '+str(prod.Pro_Sku)+' | '+str(data_e_hora_em_texto)
                        prod.save()
                        pp = Produto_Precificacao.objects.get(PP_ID=prod.Pro_Id)
                        pp.PP_custo = custo
                        pp.save()
                        sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = str(request.user), SL_ProdutoID = prod,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Master", SL_PrecoDe = custo_antigo, SL_PrecoPor = custo, SL_Estoque = 0)

        for n in range(0,len(escolha_skus)):
            try:
                prod = Produto.objects.get(Pro_Sku=str(escolha_skus[n]))
                importars(prod.Pro_Id)
            except:
                continue

        fornece = get_object_or_404(Fornecedores, pk=fornecedor)
        sinc = Nota.objects.create(NT_Num_NF=numero_nf,NT_fornecedor=fornece,NT_produtos=escolha_skus,NT_User_create=user, NT_visualizado= False)
        print(numero_nf,fornecedor,escolha_skus)

        escolha_estoque = "aa"

        escolha_fornecedor = "Todos"

        escolha_data = 0
        import datetime
        data1 = date.today()
        data2 = date.today() - datetime.timedelta(days=escolha_data)


        produto = {}
        lista_prods = []
        lista = []
        lista_def = {}
        lista_master = {}
        retorno = []
        precos=''
    # ----------------- Obter Dados de Vendas -----------------

        if escolha_data == 0:
            lista_def = {'0':0}
        else:
            vendas = Venda.objects.filter(VE_DataVenda__gte=data2, VE_DataVenda__lte=data1)
            for n in range(0,len(vendas)):
                prods_vendidos = vendas[n].VE_Itens
                for y in range(0,len(prods_vendidos)):
                    prods = prods_vendidos[y]
                    referencia = prods['ProdutoCodigo']
                    quantidade = int(str(prods['Quantidade']).replace('.00',""))
                    produto['id_master'] = referencia
                    produto['vendidos'] = quantidade
                    lista_prods.append(dict(produto))
                    lista.append(referencia)
                    
            lista = remove_repetidos(lista)
            lista_prods.sort(key=lambda x: x['id_master'], reverse=False)
            lista.sort()
            n = 0
            for n in range(0,len(lista)):
                lista_def[str(lista[n])] = 0


            n = 0
            for n in range(0,len(lista_prods)):
                ids = lista_prods[n]['id_master']
                quantidade = lista_prods[n]['vendidos']

                quant_ant = lista_def[str(ids)]
                quant_ant = quant_ant + quantidade

                lista_def[str(ids)] = quant_ant
            
    # ----------------- Obter Dados de produtos -----------------
        if len(escolha_skus) >= 1:
            for n in range(0,len(escolha_skus)):
                sku = escolha_skus[n]
                try:
                    prods = Produto.objects.get(Pro_Sku=sku)
                    ids = prods.Pro_Id
                except:
                    importars(ids)
                    prods = Produto.objects.get(Pro_Sku=sku)
                    print(ids)
                try:
                    precos = Produto_Precificacao.objects.get(PP_ID=ids)
                except:
                    continue
                n = 0
                if escolha_data != 0:
                    lista_keys = list(lista_def.keys())
                    for m in range(0,len(lista_keys)):
                        
                        if str(precos.PP_ID) == lista_keys[m] or precos.PP_ID == lista_keys[m]:
                            lista_master['N_Vendas'] = lista_def[str(precos.PP_ID)]
                            break
                        else:
                            lista_master['N_Vendas'] = 0
                
                else:
                    lista_master['N_Vendas'] = "Não calculado"

                lista_master['PP_nome'] = precos.PP_nome
                lista_master['PP_ID'] = precos.PP_ID
                lista_master['PP_sku'] = precos.PP_sku
                lista_master['PP_estoque_fisico'] = precos.PP_estoque_fisico
                lista_master['PP_fornecedor'] = str(precos.PP_fornecedor).replace('A - ','')
                lista_master['PP_custo'] = precos.PP_custo
                
                try:
                    Faixa_Site = str(precos.PP_Faixa_Site)
                    lista_master['PP_Faixa_Site'] = str(Faixa_Site)+"%"
                except:
                    lista_master['PP_Faixa_Site'] =precos.PP_Faixa_Site
                try:
                    Faixa_Portal = str(precos.PP_Faixa_Portal)
                    lista_master['PP_Faixa_Portal'] = str(Faixa_Portal)+"%"
                except:
                    lista_master['PP_Faixa_Portal'] = precos[n].PP_Faixa_Portal

                custo_adm = str(precos.PP_custo_adm_site)
                custo_adm = custo_adm.replace('0.',"")
                custo_adm = custo_adm.replace('.0',"")
                lista_master['PP_custo_adm'] = str(custo_adm)+"%"

                imposto = str(precos.PP_imposto)
                imposto = imposto.replace('0.',"")
                imposto = imposto.replace('.0',"")
                lista_master['PP_imposto'] = str(imposto)+"%"

                Lucratividade_site = str(precos.PP_comissao_site)
                Lucratividade_site = Lucratividade_site.replace('0.',"")
                Lucratividade_site = Lucratividade_site.replace('.0',"")
                lista_master['PP_Lucratividade_site'] = str(Lucratividade_site)+"%"

                lista_master['Preco_venda_atual'] = "R$ "+str(prods.Pro_PrecoVenda)
                

                retorno.append(dict(lista_master))

            retorno = sorted(retorno, key=lambda k: k['N_Vendas'], reverse=True) 

            forn = Fornecedores.objects.all().order_by('FN_Nome')
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            return render(request, 'precos/todosprecos.html',{'precos':retorno,'fornecedores':forn})

        else:
            if escolha_fornecedor == "Todos":
                if escolha_estoque == "com":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__gte= 1)
                elif escolha_estoque == "sem":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__lte= 0)
                else:
                    precos = Produto_Precificacao.objects.all()
            else:
                if escolha_estoque == "com":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__gte= 1,PP_fornecedor= str(escolha_fornecedor))
                elif escolha_estoque == "sem":
                    precos = Produto_Precificacao.objects.filter(PP_estoque_fisico__lte= 0,PP_fornecedor= str(escolha_fornecedor))
                else:
                    precos = Produto_Precificacao.objects.filter(PP_fornecedor=str(escolha_fornecedor))
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            n = 0
            print(len(precos))
            lista_keys = list(lista_def.keys())
            for n in range(0,len(precos)):
                m = 0
                for m in range(0,len(lista_keys)):
                    
                    if str(precos[n].PP_ID) == lista_keys[m] or precos[n].PP_ID == lista_keys[m]:
                        lista_master['N_Vendas'] = lista_def[str(precos[n].PP_ID)]
                        break
                    else:
                        lista_master['N_Vendas'] = 0

                prods = Produto.objects.get(Pro_Id = precos[n].PP_ID)

                lista_master['PP_nome'] = precos[n].PP_nome
                lista_master['PP_ID'] = precos[n].PP_ID
                lista_master['PP_sku'] = precos[n].PP_sku
                lista_master['PP_estoque_fisico'] = precos[n].PP_estoque_fisico
                lista_master['PP_fornecedor'] = str(precos[n].PP_fornecedor).replace('A - ','')
                lista_master['PP_custo'] = precos[n].PP_custo
                
                try:
                    Faixa_Site = str(precos[n].PP_Faixa_Site)
                    lista_master['PP_Faixa_Site'] = str(Faixa_Site)+"%"
                except:
                    lista_master['PP_Faixa_Site'] =precos[n].PP_Faixa_Site
                try:
                    Faixa_Portal = str(precos[n].PP_Faixa_Portal)
                    Faixa_Portal = str(Faixa_Portal).replace('.0',"")
                    Faixa_Portal = str(Faixa_Portal).replace('0.',"")
                    lista_master['PP_Faixa_Portal'] = str(Faixa_Portal)+"%"
                except:
                    lista_master['PP_Faixa_Portal'] = precos[n].PP_Faixa_Portal

                custo_adm = str(precos[n].PP_custo_adm_site)
                custo_adm = custo_adm.replace('0.',"")
                custo_adm = custo_adm.replace('.0',"")
                lista_master['PP_custo_adm'] = str(custo_adm)+"%"

                imposto = str(precos[n].PP_imposto)
                imposto = imposto.replace('0.',"")
                imposto = imposto.replace('.0',"")
                lista_master['PP_imposto'] = str(imposto)+"%"

                Lucratividade_site = str(precos[n].PP_comissao_site)
                Lucratividade_site = Lucratividade_site.replace('0.',"")
                Lucratividade_site = Lucratividade_site.replace('.0',"")
                lista_master['PP_Lucratividade_site'] = str(Lucratividade_site)+"%"

                lista_master['Preco_venda_atual'] = "R$ "+str(prods.Pro_PrecoVenda)
                

                retorno.append(dict(lista_master))

            retorno = sorted(retorno, key=lambda k: k['N_Vendas'], reverse=True)
            forn = Fornecedores.objects.all().order_by('FN_Nome')
            #precos = sorted(precos, key=lambda x: x.PP_estoque_fisico, reverse=True)
            return render(request, 'precos/todosprecos.html',{'precos':retorno,'fornecedores':forn})
    else:
        forn = Fornecedores.objects.all().order_by('FN_Nome')    
    return render(request, 'precos/nova_nota.html',{'fornecedores':forn})


def importars(id_master):
    from datetime import datetime
    Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
    headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
    ip = str(Master.SC_ip) #Ip ou link da api
    id_ = id_master
    url = "http://"+ip+":2082/root/produto/"+str(id_)
    response = requests.request("GET", url, headers=headers)
    response = response.text.encode('utf8')
    response = json.loads(response)
    produtos = response['produto']
    print()
    estoqueloja = 0   
    estoquebarracao = 0
    vetor = produtos[0]
    sku = vetor['Referencia']
    if sku == 'INATIVO':
        url = "http://"+ip+":2082/root/produto/" + str(vetor['Codigo']) + "/ok"
        response = requests.request("POST", url, headers=headers)
        return 0 

    url = "http://"+ip+":2082/root/estoque/"+str(vetor['Codigo'])
    response = requests.request("GET", url, headers=headers)
    response = response.text.encode('utf8')
    estoque = json.loads(response)
    estoque = estoque['estoque']
    estoque = estoque[0]
    try:
        estoque = estoque['MultiEstoque']
        for nn in range(0,len(estoque)):
            vetor2 = estoque[nn]
            local = vetor2['Localizacao']
            local = local['Nome']
            if local == 'LOJA':
                estoqueloja = float(vetor2['Saldo'])
                estoqueloja = int(estoqueloja)
            elif local == 'BARRACÃO':
                estoquebarracao = float(vetor2['Saldo'])
                estoquebarracao = int(estoquebarracao)
    except:
        estoquebarracao = float(estoque['EstoqueSite'])
        estoquebarracao = int(estoquebarracao)

    url = "http://"+ip+":2082/root/estoque/" + str(vetor['Codigo']) + "/ok"
    response = requests.request("POST", url, headers=headers)

    estoqueatual = float(vetor['EstoqueAtual'])
    estoqueatual = int(estoqueatual)

    EstoqueMaximo = float(vetor['EstoqueMaximo'])
    EstoqueMaximo = int(EstoqueMaximo)

    QuantidadeTerceiros = float(vetor['QuantidadeTerceiros'])
    QuantidadeTerceiros = int(QuantidadeTerceiros)

    if vetor['Referencia'] == '':
        nome = vetor['Codigo']
    else:
        nome = vetor['Referencia']

    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')

    name = 'Master Produto | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)

    try:
        if estoqueloja >= 1:
            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
            sku = prodss.Pro_Sku
            if sku[:2] != 'KT':
                if prodss.Pro_PrecoVenda != vetor['PrecoVenda']:
                    mudanca_preco = True
                else:
                    mudanca_preco = False
            else:
                mudanca_preco = False
        elif estoqueloja <= 0:
            mudanca_preco = False
        else:
            mudanca_preco = False

    except:
        mudanca_preco = False

    try:
        prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
        prodss.Pro_Sku = str(nome)
        prodss.Pro_Conferencia_loja = mudanca_preco
        prodss.Pro_Nome = vetor['Nome']
        prodss.Pro_EstoqueBarracao = estoquebarracao
        prodss.Pro_Loja = estoqueloja
        prodss.Pro_EstoqueTotal = estoqueatual
        prodss.Pro_Ean = vetor['EAN']
        prodss.Pro_Ativo = vetor['Ativo']
        prodss.Pro_LocalizacaoSetor = vetor['LocalizacaoSetor']
        prodss.Pro_LocalizacaoBox = vetor['LocalizacaoBox']
        prodss.Pro_SemEan = vetor['SubstituirEANPorSemGTIN']
        prodss.Pro_FornecedorCodigo = vetor['FornecedorCodigo']
        prodss.Pro_FabricanteCodigo = vetor['FabricanteCodigo']
        prodss.Pro_Classificacao = vetor['Classificacao']
        prodss.Pro_Modelo = vetor['Modelo']
        prodss.Pro_Conteudo = vetor['Conteudo']
        prodss.Pro_DescricaoCurta = vetor['DescricaoCurta']
        prodss.Pro_DescricaoLonga = vetor['DescricaoLonga']
        prodss.Pro_PrecoCusto = vetor['PrecoCusto']
        prodss.Pro_PrecoVenda = vetor['PrecoVenda']
        prodss.Pro_PrecoFicticio = str(vetor['PrecoFicticioSite'])
        prodss.Pro_Altura = vetor['Altura']
        prodss.Pro_Largura = vetor['Largura']
        prodss.Pro_Profundidade = vetor['Profundidade']
        prodss.Pro_Peso = vetor['Peso']
        prodss.Pro_NCM = vetor['NCM']
        prodss.Pro_Composicao = vetor['Composicao']
        prodss.Pro_CategoriaPrincipal = vetor['CategoriaPrincipal']
        prodss.Pro_DisponibilidadeEmEstoque = vetor['DisponibilidadeEmEstoque']
        prodss.Pro_DisponibilidadeSemEstoque = vetor['DisponibilidadeSemEstoque']
        prodss.Pro_PromocaoInicio = vetor['PromocaoInicio']
        prodss.Pro_PromocaoFim = vetor['PromocaoFim']
        prodss.Pro_PrevalecerPrecoPai = vetor['PrevalecerPrecoPai']
        prodss.Pro_Taxa = vetor['Taxa']
        prodss.Pro_NumeroMaximoParcelas = vetor['NumeroMaximoParcelas']
        prodss.Pro_EstoqueMaximo = EstoqueMaximo
        prodss.Pro_TipoDisponibilidade = vetor['TipoDisponibilidade']
        prodss.Pro_PreVenda = vetor['PreVenda']
        prodss.Pro_PreVendaData = vetor['PreVendaData']
        prodss.Pro_PreVendaLimite = vetor['PreVendaLimite']
        prodss.Pro_VendaSemEstoque = vetor['VendaSemEstoque']
        prodss.Pro_VendaSemEstoqueData = vetor['VendaSemEstoqueData']
        prodss.Pro_VendaSemEstoqueLimite = vetor['VendaSemEstoqueLimite']
        prodss.Pro_ExibirDisponibilidade = vetor['ExibirDisponibilidade']
        prodss.Pro_TipoReposicao = vetor['TipoReposicao']
        prodss.Pro_PesoCubico = vetor['PesoCubico']
        prodss.Pro_QuantidadeMaximaPorCliente = vetor['QuantidadeMaximaPorCliente']
        prodss.Pro_FreteGratis = vetor['FreteGratis']
        prodss.Pro_TituloVariacao = vetor['TituloVariacao']
        prodss.Pro_TituloSubVariacao = vetor['TituloSubVariacao']
        prodss.Pro_MetaTitle = vetor['MetaTitle']
        prodss.Pro_MetaDescription = vetor['MetaDescription']
        prodss.Pro_MetaKeywords = vetor['MetaKeywords']
        prodss.Pro_PalavrasParaPesquisa = vetor['PalavrasParaPesquisa']
        prodss.Pro_Ordem = vetor['Ordem']
        prodss.Pro_VisualizarUrlDireto = vetor['VisualizarUrlDireto']
        prodss.Pro_TemOpcaoPresente = vetor['TemOpcaoPresente']
        prodss.Pro_PresenteValor = float(vetor['PresenteValor'])
        prodss.Pro_Video = vetor['Video']
        prodss.Pro_UnidadeSigla = vetor['UnidadeSigla']
        prodss.Pro_Foto = vetor['Foto']
        prodss.Pro_ControlaEstoque = vetor['ControlaEstoque']
        prodss.Pro_Fornecedores = vetor['Fornecedores']
        prodss.Pro_Imagens = vetor['Imagens']
        prodss.Pro_CodigoPai = vetor['CodigoPai']
        prodss.Pro_EstoqueSite = vetor['EstoqueSite']
        prodss.Pro_Composto = vetor['Composto']
        prodss.Pro_Grade = vetor['Grade']
        prodss.Pro_QuantidadeTerceiros = QuantidadeTerceiros
        prodss.Pro_CST = vetor['CST']
        prodss.Pro_NomeAbreviado = vetor['NomeAbreviado']
        prodss.Pro_IPICST = vetor['IPICST']
        prodss.Pro_PISCST = vetor['PISCST']
        prodss.Pro_COFINSCST = vetor['COFINSCST']
        prodss.Pro_PISAliquota = float(vetor['PISAliquota'])
        prodss.Pro_COFINSAliquota = float(vetor['COFINSAliquota'])
        prodss.Pro_CFOPCodigo = vetor['CFOPCodigo']
        prodss.Pro_ICMSTipo = vetor['ICMSTipo']
        prodss.Pro_ICMSST = float(vetor['ICMSST'])
        prodss.Pro_CSTOrigem = vetor['CSTOrigem']
        prodss.Pro_PrecoFicticioSite = vetor['PrecoFicticioSite']
        prodss.Pro_PrecoSite = vetor['PrecoSite']
        prodss.Pro_ICMSVenda = float(vetor['ICMSVenda'])
        prodss.Pro_Volume = vetor['Volume']
        prodss.Pro_ItensInclusos = vetor['ItensInclusos']
        prodss.Pro_DadosTecnicos = vetor['DadosTecnicos']
        prodss.Pro_Categorias = vetor['Categorias']
        prodss.Pro_Unidade = vetor['Unidade']
        prodss.Pro_Thumbnail = vetor['Thumbnail']
        prodss.Pro_EnviarSite = vetor['EnviarSite']
        prodss.Pro_Comissao = vetor['Comissao']
        prodss.Pro_ExibeEsgotado = vetor['ExibeEsgotado']
        prodss.Pro_CSOSN = vetor['CSOSN']
        prodss.Pro_CEST = vetor['CEST']
        prodss.Pro_ICMSCompraAliquota = vetor['ICMSCompraAliquota']
        prodss.Pro_ICMSSTBase = vetor['ICMSSTBase']
        prodss.Pro_ICMSReducaoBaseCalculo = vetor['ICMSReducaoBaseCalculo']
        prodss.Pro_ICMSBase = vetor['ICMSBase']
        prodss.Pro_IPIAliquota = vetor['IPIAliquota']
        prodss.Pro_IPICompraAliquota = vetor['IPICompraAliquota']
        prodss.Pro_ISSAliquota = vetor['ISSAliquota']
        prodss.Pro_ISSCSERV = vetor['ISSCSERV']
        prodss.Pro_Lista = vetor['Lista']
        prodss.Pro_GrupoTributacao = vetor['GrupoTributacao']
        prodss.Pro_DefinicaoPrecoEscopo = vetor['DefinicaoPrecoEscopo']
        prodss.Pro_VtexLojasId = vetor['VtexLojasId']
        prodss.Pro_DefinicaoProdutoCodigo = vetor['DefinicaoProdutoCodigo']
        prodss.Pro_Slug = vetor['Slug']
        prodss.Pro_AtrelamentoDescricao = vetor['AtrelamentoDescricao']
        prodss.Pro_BeneficiosDescricao = vetor['BeneficiosDescricao']
        prodss.Pro_DestaqueDescricao = vetor['DestaqueDescricao']
        prodss.Pro_PromocaoDescricao = vetor['PromocaoDescricao']
        prodss.Pro_GanheBrindeDescricao = vetor['GanheBrindeDescricao']
        prodss.Pro_LancamentoDescricao = vetor['LancamentoDescricao']
        prodss.Pro_MedidasDescricao = vetor['MedidasDescricao']
        prodss.Pro_QuemUsaDescricao = vetor['QuemUsaDescricao']
        prodss.Pro_SeguroDescricao = vetor['SeguroDescricao']
        prodss.Pro_SugestaoDeUsoDescricao = vetor['SugestaoDeUsoDescricao']
        prodss.Pro_PercentualMarkupPrecoMargem = vetor['PercentualMarkupPrecoMargem']
        prodss.Pro_PrecoPercentual = vetor['PrecoPercentual']
        prodss.Pro_PrevalecerPromoPai = vetor['PrevalecerPromoPai']
        prodss.Pro_PontosFidelidade = vetor['PontosFidelidade']
        prodss.Pro_SemEntregas = vetor['SemEntregas']
        prodss.Pro_ExibirNovo = vetor['ExibirNovo']
        prodss.Pro_ExibirNovoInicio = vetor['ExibirNovoInicio']
        prodss.Pro_ExibirNovoFim = vetor['ExibirNovoFim']
        prodss.Pro_EstoqueMinimoIndisponibilizar = vetor['EstoqueMinimoIndisponibilizar']
        prodss.Pro_EstoqueMinimoNotificar = vetor['EstoqueMinimoNotificar']
        prodss.Pro_ExibirProdutoInicio = vetor['ExibirProdutoInicio']
        prodss.Pro_ExibirProdutoFim = vetor['ExibirProdutoFim']
        prodss.Pro_CoreExibirPreco = vetor['CoreExibirPreco']
        prodss.Pro_BundleOpcao = vetor['BundleOpcao']
        prodss.Pro_Flag = vetor['Flag']
        prodss.Pro_Acabamento = vetor['Acabamento']
        prodss.Pro_AnoPublicacao = vetor['AnoPublicacao']
        prodss.Pro_Assunto = vetor['Assunto']
        prodss.Pro_Autor = vetor['Autor']
        prodss.Pro_Colecao = vetor['Colecao']
        prodss.Pro_Edicao = vetor['Edicao']
        prodss.Pro_Editora = vetor['Editora']
        prodss.Pro_Formato = vetor['Formato']
        prodss.Pro_Idioma = vetor['Idioma']
        prodss.Pro_ISBN = vetor['ISBN']
        prodss.Pro_ISBN13 = vetor['ISBN13']
        prodss.Pro_Pagina = vetor['Pagina']
        prodss.Pro_Titulo = vetor['Titulo']
        prodss.Pro_Tradutor = vetor['Tradutor']
        prodss.Pro_CamposRelacionaveis = vetor['CamposRelacionaveis']
        prodss.Pro_Editor = vetor['Editor']
        prodss.Pro_Ilustrador = vetor['Ilustrador']
        prodss.Pro_Organizador = vetor['Organizador']
        prodss.Pro_Fotografo = vetor['Fotografo']
        prodss.Pro_PaisOrigem = vetor['PaisOrigem']
        prodss.Pro_DataPublicacao = vetor['DataPublicacao']
        prodss.Pro_NVolume = vetor['NVolume']
        prodss.Pro_EditaSinopse = vetor['EditaSinopse']
        prodss.Pro_BarraExtra = vetor['BarraExtra']
        prodss.save()
        print(vetor['Referencia'],'Importado Update no banco!')   
        prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
        sinc = Sinc_log.objects.create(SL_Nome = name, SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoVenda'], SL_PrecoPor = vetor['PrecoFicticioSite'], SL_Estoque = 0)


    except Produto.DoesNotExist:
        Produto(Pro_Id = vetor['Codigo'], Pro_Sku = str(nome), Pro_Nome = vetor['Nome'], Pro_EstoqueBarracao = estoquebarracao, Pro_Loja = estoqueloja, Pro_EstoqueTotal = estoqueatual, Pro_Ean = vetor['EAN'], Pro_Ativo = vetor['Ativo'], Pro_LocalizacaoSetor = vetor['LocalizacaoSetor'], Pro_LocalizacaoBox = vetor['LocalizacaoBox'], Pro_SemEan = vetor['SubstituirEANPorSemGTIN'], Pro_FornecedorCodigo = vetor['FornecedorCodigo'], Pro_FabricanteCodigo = vetor['FabricanteCodigo'], Pro_Classificacao = vetor['Classificacao'], Pro_Modelo = vetor['Modelo'], Pro_Conteudo = vetor['Conteudo'], Pro_DescricaoCurta = vetor['DescricaoCurta'], Pro_DescricaoLonga = vetor['DescricaoLonga'], Pro_PrecoCusto = vetor['PrecoCusto'], Pro_PrecoVenda = vetor['PrecoVenda'], Pro_PrecoFicticio = str(vetor['PrecoFicticioSite']), Pro_Altura = vetor['Altura'], Pro_Largura = vetor['Largura'], Pro_Profundidade = vetor['Profundidade'], Pro_Peso = vetor['Peso'], Pro_NCM = vetor['NCM'], Pro_Composicao = vetor['Composicao'], Pro_CategoriaPrincipal = vetor['CategoriaPrincipal'], Pro_DisponibilidadeEmEstoque = vetor['DisponibilidadeEmEstoque'], Pro_DisponibilidadeSemEstoque = vetor['DisponibilidadeSemEstoque'], Pro_PromocaoInicio = vetor['PromocaoInicio'], Pro_PromocaoFim = vetor['PromocaoFim'], Pro_PrevalecerPrecoPai = vetor['PrevalecerPrecoPai'], Pro_Taxa = vetor['Taxa'], Pro_NumeroMaximoParcelas = vetor['NumeroMaximoParcelas'], Pro_EstoqueMaximo = EstoqueMaximo, Pro_TipoDisponibilidade = vetor['TipoDisponibilidade'], Pro_PreVenda = vetor['PreVenda'], Pro_PreVendaData = vetor['PreVendaData'], Pro_PreVendaLimite = vetor['PreVendaLimite'], Pro_VendaSemEstoque = vetor['VendaSemEstoque'], Pro_VendaSemEstoqueData = vetor['VendaSemEstoqueData'], Pro_VendaSemEstoqueLimite = vetor['VendaSemEstoqueLimite'], Pro_ExibirDisponibilidade = vetor['ExibirDisponibilidade'], Pro_TipoReposicao = vetor['TipoReposicao'], Pro_PesoCubico = vetor['PesoCubico'], Pro_QuantidadeMaximaPorCliente = vetor['QuantidadeMaximaPorCliente'], Pro_FreteGratis = vetor['FreteGratis'], Pro_TituloVariacao = vetor['TituloVariacao'], Pro_TituloSubVariacao = vetor['TituloSubVariacao'], Pro_MetaTitle = vetor['MetaTitle'], Pro_MetaDescription = vetor['MetaDescription'], Pro_MetaKeywords = vetor['MetaKeywords'], Pro_PalavrasParaPesquisa = vetor['PalavrasParaPesquisa'], Pro_Ordem = vetor['Ordem'], Pro_VisualizarUrlDireto = vetor['VisualizarUrlDireto'], Pro_TemOpcaoPresente = vetor['TemOpcaoPresente'], Pro_PresenteValor = float(vetor['PresenteValor']), Pro_Video = vetor['Video'], Pro_UnidadeSigla = vetor['UnidadeSigla'], Pro_Foto = vetor['Foto'], Pro_ControlaEstoque = vetor['ControlaEstoque'], Pro_Fornecedores = vetor['Fornecedores'], Pro_Imagens = vetor['Imagens'], Pro_CodigoPai = vetor['CodigoPai'], Pro_EstoqueSite = vetor['EstoqueSite'], Pro_Composto = vetor['Composto'], Pro_Grade = vetor['Grade'], Pro_QuantidadeTerceiros = QuantidadeTerceiros, Pro_CST = vetor['CST'], Pro_NomeAbreviado = vetor['NomeAbreviado'], Pro_IPICST = vetor['IPICST'], Pro_PISCST = vetor['PISCST'], Pro_COFINSCST = vetor['COFINSCST'], Pro_PISAliquota = float(vetor['PISAliquota']), Pro_COFINSAliquota = float(vetor['COFINSAliquota']), Pro_CFOPCodigo = vetor['CFOPCodigo'], Pro_ICMSTipo = vetor['ICMSTipo'], Pro_ICMSST = float(vetor['ICMSST']), Pro_CSTOrigem = vetor['CSTOrigem'], Pro_PrecoFicticioSite = vetor['PrecoFicticioSite'], Pro_PrecoSite = vetor['PrecoSite'], Pro_ICMSVenda = float(vetor['ICMSVenda']), Pro_Volume = vetor['Volume'], Pro_ItensInclusos = vetor['ItensInclusos'], Pro_DadosTecnicos = vetor['DadosTecnicos'], Pro_Categorias = vetor['Categorias'], Pro_Unidade = vetor['Unidade'], Pro_Thumbnail = vetor['Thumbnail'], Pro_EnviarSite = vetor['EnviarSite'], Pro_Comissao = vetor['Comissao'], Pro_ExibeEsgotado = vetor['ExibeEsgotado'], Pro_CSOSN = vetor['CSOSN'], Pro_CEST = vetor['CEST'], Pro_ICMSCompraAliquota = vetor['ICMSCompraAliquota'], Pro_ICMSSTBase = vetor['ICMSSTBase'], Pro_ICMSReducaoBaseCalculo = vetor['ICMSReducaoBaseCalculo'], Pro_ICMSBase = vetor['ICMSBase'], Pro_IPIAliquota = vetor['IPIAliquota'], Pro_IPICompraAliquota = vetor['IPICompraAliquota'], Pro_ISSAliquota = vetor['ISSAliquota'], Pro_ISSCSERV = vetor['ISSCSERV'], Pro_Lista = vetor['Lista'], Pro_GrupoTributacao = vetor['GrupoTributacao'], Pro_DefinicaoPrecoEscopo = vetor['DefinicaoPrecoEscopo'], Pro_VtexLojasId = vetor['VtexLojasId'], Pro_DefinicaoProdutoCodigo = vetor['DefinicaoProdutoCodigo'], Pro_Slug = vetor['Slug'], Pro_AtrelamentoDescricao = vetor['AtrelamentoDescricao'], Pro_BeneficiosDescricao = vetor['BeneficiosDescricao'], Pro_DestaqueDescricao = vetor['DestaqueDescricao'], Pro_PromocaoDescricao = vetor['PromocaoDescricao'], Pro_GanheBrindeDescricao = vetor['GanheBrindeDescricao'], Pro_LancamentoDescricao = vetor['LancamentoDescricao'], Pro_MedidasDescricao = vetor['MedidasDescricao'], Pro_QuemUsaDescricao = vetor['QuemUsaDescricao'], Pro_SeguroDescricao = vetor['SeguroDescricao'], Pro_SugestaoDeUsoDescricao = vetor['SugestaoDeUsoDescricao'], Pro_PercentualMarkupPrecoMargem = vetor['PercentualMarkupPrecoMargem'], Pro_PrecoPercentual = vetor['PrecoPercentual'], Pro_PrevalecerPromoPai = vetor['PrevalecerPromoPai'], Pro_PontosFidelidade = vetor['PontosFidelidade'], Pro_SemEntregas = vetor['SemEntregas'], Pro_ExibirNovo = vetor['ExibirNovo'], Pro_ExibirNovoInicio = vetor['ExibirNovoInicio'], Pro_ExibirNovoFim = vetor['ExibirNovoFim'], Pro_EstoqueMinimoIndisponibilizar = vetor['EstoqueMinimoIndisponibilizar'], Pro_EstoqueMinimoNotificar = vetor['EstoqueMinimoNotificar'], Pro_ExibirProdutoInicio = vetor['ExibirProdutoInicio'], Pro_ExibirProdutoFim = vetor['ExibirProdutoFim'], Pro_CoreExibirPreco = vetor['CoreExibirPreco'], Pro_BundleOpcao = vetor['BundleOpcao'], Pro_Flag = vetor['Flag'], Pro_Acabamento = vetor['Acabamento'], Pro_AnoPublicacao = vetor['AnoPublicacao'], Pro_Assunto = vetor['Assunto'], Pro_Autor = vetor['Autor'], Pro_Colecao = vetor['Colecao'], Pro_Edicao = vetor['Edicao'], Pro_Editora = vetor['Editora'], Pro_Formato = vetor['Formato'], Pro_Idioma = vetor['Idioma'], Pro_ISBN = vetor['ISBN'], Pro_ISBN13 = vetor['ISBN13'], Pro_Pagina = vetor['Pagina'], Pro_Titulo = vetor['Titulo'], Pro_Tradutor = vetor['Tradutor'], Pro_CamposRelacionaveis = vetor['CamposRelacionaveis'], Pro_Editor = vetor['Editor'], Pro_Ilustrador = vetor['Ilustrador'], Pro_Organizador = vetor['Organizador'], Pro_Fotografo = vetor['Fotografo'], Pro_PaisOrigem = vetor['PaisOrigem'], Pro_DataPublicacao = vetor['DataPublicacao'], Pro_NVolume = vetor['NVolume'], Pro_EditaSinopse = vetor['EditaSinopse'], Pro_BarraExtra = vetor['BarraExtra']).save()
        prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
        sinc = Sinc_log.objects.create(SL_Nome = name, SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoFicticioSite'], SL_PrecoPor = vetor['PrecoVenda'], SL_Estoque = 0)
        print(vetor['Referencia'],'Importado Cadastrado no banco!')

    if vetor['FabricanteCodigo'] == 916 or vetor['FabricanteCodigo'] == '916':
        data = {}
        data['SKU'] = vetor['Referencia']
        data['ID_master'] = vetor['Codigo']
        data['Titulo'] = vetor['Nome']
        data['Preco_tabela'] = vetor['PrecoVenda']      

        db.child("Produtos").child(vetor['Referencia']).set(data)
        print(vetor['Referencia'],'arrigo')

    custo = vetor['PrecoCusto']
    custo = custo.replace('"','')
    custo = custo.replace("'","")
    custo = float(custo)

    try:
        comiss = get_object_or_404(Comissoes, pk='1')
        PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))
        PRO_LUC.PP_custo = custo
        try:
            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])                
            fornecedor = prodss.Pro_Fornecedores
            fornecedor = json.dumps(fornecedor)
            fornecedor = json.loads(fornecedor)                
            fornecedor = fornecedor[0]
            fornecedor = fornecedor['FornecedorCodigo']
            forn = Fornecedores.objects.get(FN_ID = fornecedor)
            fornecedor = forn.FN_Nome
        except:
            fornecedor = 'Não informado'

        #print(fornecedor)
        PRO_LUC.PP_fornecedor = fornecedor

        if PRO_LUC.PP_Classificao_total_absoluta != True:

            if PRO_LUC.PP_comissao_site_absoluta != True:
                PRO_LUC.PP_comissao_site = comiss.CS_Comissao_site
            
            if PRO_LUC.PP_Amazon_KES_absoluta != True:
                PRO_LUC.PP_Amazon_KES = comiss.CS_Amazon_Comissao
            
            if PRO_LUC.PP_B2W_ALK_absoluta != True:
                PRO_LUC.PP_B2W_ALK = comiss.CS_B2W_ALK_Comissao

            if PRO_LUC.PP_B2W_GEA_absoluta != True:
                PRO_LUC.PP_B2W_GEA = comiss.CS_B2W_GEA_Comissao                                

            if PRO_LUC.PP_B2W_JCMA_absoluta != True:
                PRO_LUC.PP_B2W_JCMA = comiss.CS_B2W_JCMA_Comissao

            if PRO_LUC.PP_B2W_KC_absoluta != True:
                PRO_LUC.PP_B2W_KC = comiss.CS_B2W_KC_Comissao

            if PRO_LUC.PP_Carrefour_ALK_absoluta != True:
                PRO_LUC.PP_Carrefour_ALK = comiss.CS_Carrefour_ALK_Comissao

            if PRO_LUC.PP_Carrefour_GEA_absoluta != True:
                PRO_LUC.PP_Carrefour_GEA = comiss.CS_Carrefour_GEA_Comissao

            if PRO_LUC.PP_Centauro_ALK_absoluta != True:
                PRO_LUC.PP_Centauro_ALK = comiss.CS_Centauro_ALK_Comissao

            if PRO_LUC.PP_Cnova_KES_absoluta != True:
                PRO_LUC.PP_Cnova_KES = comiss.CS_Cnova_KES_Comissao

            if PRO_LUC.PP_MadeiraMadeira_KES_absoluta != True:
                PRO_LUC.PP_MadeiraMadeira_KES = comiss.CS_MM_KES_Comissao

            if PRO_LUC.PP_Magalu_GEA_absoluta != True:
                PRO_LUC.PP_Magalu_GEA = comiss.CS_Magalu_GEA_Comissao

            if PRO_LUC.PP_Magalu_KC_absoluta != True:
                PRO_LUC.PP_Magalu_KC = comiss.CS_Magalu_KC_Comissao
            
            if PRO_LUC.PP_Netshoes_KES_absoluta != True:
                PRO_LUC.PP_Netshoes_KES = comiss.CS_Netshoes_KES_Comissao
            
            if PRO_LUC.PP_Netshoes_ALK_absoluta != True:
                PRO_LUC.PP_Netshoes_ALK = comiss.CS_Netshoes_ALK_Comissao
            
            Master_LocalizacaoSetor = vetor['LocalizacaoSetor']
            Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace('"','')
            Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace("'","")

            if PRO_LUC.PP_Faixa_Portal_absoluta != True:

                if Master_LocalizacaoSetor == "A":
                    try:
                        precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                        a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                        a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                        a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                        a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                        a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                        a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                        a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                        a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                        a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                        a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                        a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                        a400_a_449_99 = float(precofaixa.PF_400_a_449_99)
                        a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                        a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                        a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                        a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                        a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                        maior_3000 = float(precofaixa.PF_maior_3000)
                    except:
                        a0_a_4_99 = 30
                        a5_a_14_99 = 28
                        a15_a_29_99 = 15                             
                        a30_a_49_99 = 0
                        a50_a_79_99 = 0
                        a80_a_119_99 = 0
                        a120_a_149_99 = 0
                        a150_a_199_99 = 0
                        a200_a_249_99 = 0
                        a250_a_299_99 = 0
                        a300_a_349_99 = 0
                        a350_a_399_99 = 0
                        a400_a_449_99 = 0
                        a450_a_549_99 = 0
                        a550_a_649_99 = 0
                        a650_a_749_99 = 0
                        a750_a_899_99 = 0
                        a900_a_999_99 = 0
                        a1000_a_1499_99 = 0
                        a1500_a_1999_99 = 0
                        a2000_a_2499_99 = 0
                        a2500_a_2999_99 = 0
                        maior_3000 = 0
                elif Master_LocalizacaoSetor == 'B':
                    try:
                        precofaixa = Preco_Faixa.objects.get(PF_ID = '6')
                        a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                        a5_a_14_99 = float(precofaixa.PF_5_a_14_99)
                        a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                        a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                        a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                        a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                        a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                        a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                        a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                        a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                        a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                        a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                        a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                        a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                        a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                        a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                        a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                        maior_3000 = float(precofaixa.PF_maior_3000)
                    except:
                        a0_a_4_99 = 40
                        a5_a_14_99 = 35
                        a15_a_29_99 = 25                             
                        a30_a_49_99 = 20
                        a50_a_79_99 = 15
                        a80_a_119_99 = 13
                        a120_a_149_99 = 11
                        a150_a_199_99 = 10
                        a200_a_249_99 = 9
                        a250_a_299_99 = 8
                        a300_a_349_99 = 7.5
                        a350_a_399_99 = 7
                        a400_a_449_99 = 6.5
                        a450_a_549_99 = 6
                        a550_a_649_99 = 5.5
                        a650_a_749_99 = 5
                        a750_a_899_99 = 4.5
                        a900_a_999_99 = 4
                        a1000_a_1499_99 = 3.5
                        a1500_a_1999_99 = 3
                        a2000_a_2499_99 = 3
                        a2500_a_2999_99 = 3
                        maior_3000 = 3
                else:
                    a0_a_4_99 = 40
                    a5_a_14_99 = 35
                    a15_a_29_99 = 25                             
                    a30_a_49_99 = 20
                    a50_a_79_99 = 15
                    a80_a_119_99 = 13
                    a120_a_149_99 = 11
                    a150_a_199_99 = 10
                    a200_a_249_99 = 9
                    a250_a_299_99 = 8
                    a300_a_349_99 = 7.5
                    a350_a_399_99 = 7
                    a400_a_449_99 = 6.5
                    a450_a_549_99 = 6
                    a550_a_649_99 = 5.5
                    a650_a_749_99 = 5
                    a750_a_899_99 = 4.5
                    a900_a_999_99 = 4
                    a1000_a_1499_99 = 35
                    a1500_a_1999_99 = 3
                    a2000_a_2499_99 = 3
                    a2500_a_2999_99 = 3
                    maior_3000 = 3

                if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                    if custo <= 4.99:
                        classificacao = a0_a_4_99

                    elif custo >= 5 and custo <= 14.99:
                        classificacao = a5_a_14_99

                    elif custo >= 15 and custo <= 29.99:
                        classificacao = a15_a_29_99

                    elif custo >= 30 and custo <= 49.99:
                        classificacao = a30_a_49_99

                    elif custo >= 50 and custo <= 79.99:
                        classificacao = a50_a_79_99

                    elif custo >= 80 and custo <= 119.99:
                        classificacao = a80_a_119_99

                    elif custo >= 120 and custo <= 149.99:
                        classificacao = a120_a_149_99

                    elif custo >= 150 and custo <= 199.99:
                        classificacao = a150_a_199_99

                    elif custo >= 200 and custo <= 249.99:
                        classificacao = a200_a_249_99
                        
                    elif custo >= 250 and custo <= 299.99:
                        classificacao = a250_a_299_99

                    elif custo >= 300 and custo <= 349.99:
                        classificacao = a300_a_349_99

                    elif custo >= 350 and custo <= 399.99:
                        classificacao = a350_a_399_99

                    elif custo >= 400 and custo <= 449.99:
                        classificacao = a400_a_449_99

                    elif custo >= 450 and custo <= 549.99:
                        classificacao = a450_a_549_99

                    elif custo >= 550 and custo <= 649.99:
                        classificacao = a550_a_649_99

                    elif custo >= 650 and custo <= 749.99:
                        classificacao = a650_a_749_99

                    elif custo >= 750 and custo <= 899.99:
                        classificacao = a750_a_899_99

                    elif custo >= 900 and custo <= 999.99:
                        classificacao = a900_a_999_99

                    elif custo >= 1000 and custo <= 1499.99:
                        classificacao = a1000_a_1499_99

                    elif custo >= 1500 and custo <= 1999.99:
                        classificacao = a1500_a_1999_99

                    elif custo >= 2000 and custo <= 2499.99:
                        classificacao = a2000_a_2499_99

                    elif custo >= 2500 and custo <= 2999.99:
                        classificacao = a2500_a_2999_99

                    elif custo >= 3000:
                        classificacao = maior_3000

                else:
                    classificacao = '00'
            
                PRO_LUC.PP_Faixa_Portal = classificacao
            
            if PRO_LUC.PP_Faixa_Site_absoluta != True:
                if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
                    try:
                        faixa = Preco_Faixa.objects.get(PF_ID = '2')

                        a0_a_4_99 = float(faixa.PF_0_a_4_99)

                        a5_a_14_99 = float(faixa.PF_5_a_14_99)

                        a15_a_29_99 = float(faixa.PF_15_a_29_99)
                        
                        a30_a_49_99 = float(faixa.PF_30_a_49_99)

                        a50_a_79_99 = float(faixa.PF_50_a_79_99)

                        a80_a_119_99 = float(faixa.PF_80_a_119_99)

                        a120_a_149_99 = float(faixa.PF_120_a_149_99)
                        a150_a_199_99 = float(faixa.PF_150_a_199_99)

                        a200_a_249_99 = float(faixa.PF_200_a_249_99)

                        a250_a_299_99 = float(faixa.PF_250_a_299_99)

                        a300_a_349_99 = float(faixa.PF_300_a_349_99)
                        a350_a_399_99 = float(faixa.PF_350_a_399_99)
                        a400_a_449_99 = float(faixa.PF_400_a_449_99)

                        a450_a_549_99 = float(faixa.PF_450_a_549_99)

                        a550_a_649_99 = float(faixa.PF_550_a_649_99)

                        a650_a_749_99 = float(faixa.PF_650_a_749_99)

                        a750_a_899_99 = float(faixa.PF_750_a_899_99)

                        a900_a_999_99 = float(faixa.PF_900_a_999_99)

                        a1000_a_1499_99 = float(faixa.PF_1000_a_1499_99)

                        a1500_a_1999_99 = float(faixa.PF_1500_a_1999_99)

                        a2000_a_2499_99 = float(faixa.PF_2000_a_2499_99)

                        a2500_a_2999_99 = float(faixa.PF_2500_a_2999_99)

                        maior_3000 = float(faixa.PF_maior_3000)

                    except:
                        a0_a_4_99 = 30
                        a5_a_14_99 = 15
                        a15_a_29_99 = 10                                    
                        a30_a_49_99 = 8
                        a50_a_79_99 = 7
                        a80_a_119_99 = 5
                        a120_a_149_99 = 3
                        a150_a_199_99 = 3
                        a200_a_249_99 = 3
                        a250_a_299_99 = 3
                        a300_a_349_99 = 3
                        a350_a_399_99 = 3
                        a400_a_449_99 = 3
                        a450_a_549_99 = 3
                        a550_a_649_99 = 3
                        a650_a_749_99 = 3
                        a750_a_899_99 = 3
                        a900_a_999_99 = 2
                        a1000_a_1499_99 = 1
                        a1500_a_1999_99 = 1
                        a2000_a_2499_99 = 1
                        a2500_a_2999_99 = 1
                        maior_3000 = 1

                    if custo <= 4.99:
                        classificacao = a0_a_4_99

                    elif custo >= 5 and custo <= 14.99:
                        classificacao = a5_a_14_99

                    elif custo >= 15 and custo <= 29.99:
                        classificacao = a15_a_29_99

                    elif custo >= 30 and custo <= 49.99:
                        classificacao = a30_a_49_99

                    elif custo >= 50 and custo <= 79.99:
                        classificacao = a50_a_79_99

                    elif custo >= 80 and custo <= 119.99:
                        classificacao = a80_a_119_99

                    elif custo >= 120 and custo <= 149.99:
                        classificacao = a120_a_149_99

                    elif custo >= 150 and custo <= 199.99:
                        classificacao = a150_a_199_99

                    elif custo >= 200 and custo <= 249.99:
                        classificacao = a200_a_249_99
                        
                    elif custo >= 250 and custo <= 299.99:
                        classificacao = a250_a_299_99

                    elif custo >= 300 and custo <= 349.99:
                        classificacao = a300_a_349_99

                    elif custo >= 350 and custo <= 399.99:
                        classificacao = a350_a_399_99

                    elif custo >= 400 and custo <= 449.99:
                        classificacao = a400_a_449_99

                    elif custo >= 450 and custo <= 549.99:
                        classificacao = a450_a_549_99

                    elif custo >= 550 and custo <= 649.99:
                        classificacao = a550_a_649_99

                    elif custo >= 650 and custo <= 749.99:
                        classificacao = a650_a_749_99

                    elif custo >= 750 and custo <= 899.99:
                        classificacao = a750_a_899_99

                    elif custo >= 900 and custo <= 999.99:
                        classificacao = a900_a_999_99

                    elif custo >= 1000 and custo <= 1499.99:
                        classificacao = a1000_a_1499_99

                    elif custo >= 1500 and custo <= 1999.99:
                        classificacao = a1500_a_1999_99

                    elif custo >= 2000 and custo <= 2499.99:
                        classificacao = a2000_a_2499_99

                    elif custo >= 2500 and custo <= 2999.99:
                        classificacao = a2500_a_2999_99

                    elif custo >= 3000:
                        classificacao = maior_3000
                        
                else:
                    classificacao = '00'

                PRO_LUC.PP_Faixa_Site = classificacao


            PRO_LUC.save()
            #print('alterado')

    except:
        try:
            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])                
            fornecedor = prodss.Pro_Fornecedores
            fornecedor = json.dumps(fornecedor)
            fornecedor = json.loads(fornecedor)                
            fornecedor = fornecedor[0]
            fornecedor = fornecedor['FornecedorCodigo']
            forn = Fornecedores.objects.get(FN_ID = fornecedor)
            fornecedor = forn.FN_Nome
        except:
            fornecedor = 'Não informado'

        #print(fornecedor)
        Master_LocalizacaoSetor = vetor['LocalizacaoSetor']
        Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace('"','')
        Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace("'","")

        if Master_LocalizacaoSetor == "A":
            try:
                precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                
                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                maior_3000 = float(precofaixa.PF_maior_3000)
            except:
                a0_a_4_99 = 30
                a5_a_14_99 = 28
                a15_a_29_99 = 15                             
                a30_a_49_99 = 0
                a50_a_79_99 = 0
                a80_a_119_99 = 0
                a120_a_149_99 = 0
                a150_a_199_99 = 0
                a200_a_249_99 = 0
                a250_a_299_99 = 0
                a300_a_349_99 = 0
                a350_a_399_99 = 0
                a400_a_449_99 = 0
                a450_a_549_99 = 0
                a550_a_649_99 = 0
                a650_a_749_99 = 0
                a750_a_899_99 = 0
                a900_a_999_99 = 0
                a1000_a_1499_99 = 0
                a1500_a_1999_99 = 0
                a2000_a_2499_99 = 0
                a2500_a_2999_99 = 0
                maior_3000 = 0
        elif Master_LocalizacaoSetor == 'B':
            try:
                precofaixa = Preco_Faixa.objects.get(PF_ID = '6')
                a0_a_4_99 = float(precofaixa.PF_0_a_4_99)

                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)

                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                
                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)

                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)

                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)

                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)

                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)

                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)

                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)

                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)

                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)

                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)

                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)

                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)

                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)

                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)

                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)

                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)

                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)

                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)

                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)

                maior_3000 = float(precofaixa.PF_maior_3000)
            except:
                a0_a_4_99 = 40
                a5_a_14_99 = 35
                a15_a_29_99 = 25                             
                a30_a_49_99 = 20
                a50_a_79_99 = 15
                a80_a_119_99 = 13
                a120_a_149_99 = 11
                a150_a_199_99 = 10
                a200_a_249_99 = 9
                a250_a_299_99 = 8
                a300_a_349_99 = 7.5
                a350_a_399_99 = 7
                a400_a_449_99 = 6.5
                a450_a_549_99 = 6
                a550_a_649_99 = 5.5
                a650_a_749_99 = 5
                a750_a_899_99 = 4.5
                a900_a_999_99 = 4
                a1000_a_1499_99 = 3.5
                a1500_a_1999_99 = 3
                a2000_a_2499_99 = 3
                a2500_a_2999_99 = 3
                maior_3000 = 3
        else:
            a0_a_4_99 = 40
            a5_a_14_99 = 35
            a15_a_29_99 = 25                             
            a30_a_49_99 = 20
            a50_a_79_99 = 15
            a80_a_119_99 = 13
            a120_a_149_99 = 11
            a150_a_199_99 = 10
            a200_a_249_99 = 9
            a250_a_299_99 = 8
            a300_a_349_99 = 7.5
            a350_a_399_99 = 7
            a400_a_449_99 = 6.5
            a450_a_549_99 = 6
            a550_a_649_99 = 5.5
            a650_a_749_99 = 5
            a750_a_899_99 = 4.5
            a900_a_999_99 = 4
            a1000_a_1499_99 = 3.5
            a1500_a_1999_99 = 3
            a2000_a_2499_99 = 3
            a2500_a_2999_99 = 3
            maior_3000 = 3
        if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
            if custo <= 4.99:
                classificacao = a0_a_4_99

            elif custo >= 5 and custo <= 14.99:
                classificacao = a5_a_14_99

            elif custo >= 15 and custo <= 29.99:
                classificacao = a15_a_29_99

            elif custo >= 30 and custo <= 49.99:
                classificacao = a30_a_49_99

            elif custo >= 50 and custo <= 79.99:
                classificacao = a50_a_79_99

            elif custo >= 80 and custo <= 119.99:
                classificacao = a80_a_119_99

            elif custo >= 120 and custo <= 149.99:
                classificacao = a120_a_149_99

            elif custo >= 150 and custo <= 199.99:
                classificacao = a150_a_199_99

            elif custo >= 200 and custo <= 249.99:
                classificacao = a200_a_249_99
                
            elif custo >= 250 and custo <= 299.99:
                classificacao = a250_a_299_99

            elif custo >= 300 and custo <= 349.99:
                classificacao = a300_a_349_99

            elif custo >= 350 and custo <= 399.99:
                classificacao = a350_a_399_99

            elif custo >= 400 and custo <= 449.99:
                classificacao = a400_a_449_99

            elif custo >= 450 and custo <= 549.99:
                classificacao = a450_a_549_99

            elif custo >= 550 and custo <= 649.99:
                classificacao = a550_a_649_99

            elif custo >= 650 and custo <= 749.99:
                classificacao = a650_a_749_99

            elif custo >= 750 and custo <= 899.99:
                classificacao = a750_a_899_99

            elif custo >= 900 and custo <= 999.99:
                classificacao = a900_a_999_99

            elif custo >= 1000 and custo <= 1499.99:
                classificacao = a1000_a_1499_99

            elif custo >= 1500 and custo <= 1999.99:
                classificacao = a1500_a_1999_99

            elif custo >= 2000 and custo <= 2499.99:
                classificacao = a2000_a_2499_99

            elif custo >= 2500 and custo <= 2999.99:
                classificacao = a2500_a_2999_99

            elif custo >= 3000:
                classificacao = maior_3000
        else:
            classificacao = '00'

        faixa_portal = classificacao

        if vetor['FabricanteCodigo'] != '916' or vetor['FabricanteCodigo'] != 916:
            try:
                faixa = Preco_Faixa.objects.get(PF_ID = '2')

                a0_a_4_99 = float(faixa.PF_0_a_4_99)

                a5_a_14_99 = float(faixa.PF_5_a_14_99)

                a15_a_29_99 = float(faixa.PF_15_a_29_99)
                
                a30_a_49_99 = float(faixa.PF_30_a_49_99)

                a50_a_79_99 = float(faixa.PF_50_a_79_99)

                a80_a_119_99 = float(faixa.PF_80_a_119_99)

                a120_a_149_99 = float(faixa.PF_120_a_149_99)

                a150_a_199_99 = float(faixa.PF_150_a_199_99)

                a200_a_249_99 = float(faixa.PF_200_a_249_99)

                a250_a_299_99 = float(faixa.PF_250_a_299_99)

                a300_a_349_99 = float(faixa.PF_300_a_349_99)

                a350_a_399_99 = float(faixa.PF_350_a_399_99)

                a400_a_449_99 = float(faixa.PF_400_a_449_99)

                a450_a_549_99 = float(faixa.PF_450_a_549_99)

                a550_a_649_99 = float(faixa.PF_550_a_649_99)

                a650_a_749_99 = float(faixa.PF_650_a_749_99)

                a750_a_899_99 = float(faixa.PF_750_a_899_99)

                a900_a_999_99 = float(faixa.PF_900_a_999_99)

                a1000_a_1499_99 = float(faixa.PF_1000_a_1499_99)

                a1500_a_1999_99 = float(faixa.PF_1500_a_1999_99)

                a2000_a_2499_99 = float(faixa.PF_2000_a_2499_99)

                a2500_a_2999_99 = float(faixa.PF_2500_a_2999_99)

                maior_3000 = float(faixa.PF_maior_3000)

            except:
                a0_a_4_99 = 30
                a5_a_14_99 = 15
                a15_a_29_99 = 10                                    
                a30_a_49_99 = 8
                a50_a_79_99 = 7
                a80_a_119_99 = 5
                a120_a_149_99 = 3
                a150_a_199_99 = 3
                a200_a_249_99 = 3
                a250_a_299_99 = 3
                a300_a_349_99 = 3
                a350_a_399_99 = 3
                a400_a_449_99 = 3
                a450_a_549_99 = 3
                a550_a_649_99 = 3
                a650_a_749_99 = 3
                a750_a_899_99 = 3
                a900_a_999_99 = 2
                a1000_a_1499_99 = 1
                a1500_a_1999_99 = 1
                a2000_a_2499_99 = 1
                a2500_a_2999_99 = 1
                maior_3000 = 1

            if custo <= 4.99:
                classificacao = a0_a_4_99

            elif custo >= 5 and custo <= 14.99:
                classificacao = a5_a_14_99

            elif custo >= 15 and custo <= 29.99:
                classificacao = a15_a_29_99

            elif custo >= 30 and custo <= 49.99:
                classificacao = a30_a_49_99

            elif custo >= 50 and custo <= 79.99:
                classificacao = a50_a_79_99

            elif custo >= 80 and custo <= 119.99:
                classificacao = a80_a_119_99

            elif custo >= 120 and custo <= 149.99:
                classificacao = a120_a_149_99

            elif custo >= 150 and custo <= 199.99:
                classificacao = a150_a_199_99

            elif custo >= 200 and custo <= 249.99:
                classificacao = a200_a_249_99
                
            elif custo >= 250 and custo <= 299.99:
                classificacao = a250_a_299_99

            elif custo >= 300 and custo <= 349.99:
                classificacao = a300_a_349_99

            elif custo >= 350 and custo <= 399.99:
                classificacao = a350_a_399_99

            elif custo >= 400 and custo <= 449.99:
                classificacao = a400_a_449_99

            elif custo >= 450 and custo <= 549.99:
                classificacao = a450_a_549_99

            elif custo >= 550 and custo <= 649.99:
                classificacao = a550_a_649_99

            elif custo >= 650 and custo <= 749.99:
                classificacao = a650_a_749_99

            elif custo >= 750 and custo <= 899.99:
                classificacao = a750_a_899_99

            elif custo >= 900 and custo <= 999.99:
                classificacao = a900_a_999_99

            elif custo >= 1000 and custo <= 1499.99:
                classificacao = a1000_a_1499_99

            elif custo >= 1500 and custo <= 1999.99:
                classificacao = a1500_a_1999_99

            elif custo >= 2000 and custo <= 2499.99:
                classificacao = a2000_a_2499_99

            elif custo >= 2500 and custo <= 2999.99:
                classificacao = a2500_a_2999_99

            elif custo >= 3000:
                classificacao = maior_3000
                
        else:
            classificacao = '00'

        faixa_site = classificacao
        create = Produto_Precificacao.objects.create(PP_ID = int(vetor['Codigo']),PP_sku = prodss, PP_nome = str(vetor['Nome']), PP_estoque_fisico = int(estoqueatual), PP_fornecedor = str(fornecedor), PP_custo = float(custo), PP_custo_adm_portal = float(comiss.CS_Custo_Adm_portal), PP_imposto = float(comiss.CS_Impostos), PP_Classificao_total_absoluta = False, PP_Classificao_total = 0, PP_comissao_site_absoluta = False, PP_comissao_site = float(comiss.CS_Comissao_site), PP_Faixa_Portal = faixa_portal, PP_Faixa_Site = faixa_site,PP_Amazon_KES_absoluta = False, PP_Amazon_KES = float(comiss.CS_Amazon_Comissao), PP_B2W_ALK_absoluta = False, PP_B2W_ALK = float(comiss.CS_B2W_ALK_Comissao), PP_B2W_GEA_absoluta = False, PP_B2W_GEA = float(comiss.CS_B2W_GEA_Comissao), PP_B2W_JCMA_absoluta = False, PP_B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao), PP_B2W_KC_absoluta = False, PP_B2W_KC = float(comiss.CS_B2W_KC_Comissao), PP_Carrefour_ALK_absoluta = False, PP_Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao), PP_Carrefour_GEA_absoluta = False, PP_Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao), PP_Centauro_ALK_absoluta = False, PP_Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao), PP_Cnova_KES_absoluta = False, PP_Cnova_KES = float(comiss.CS_Cnova_KES_Comissao), PP_MadeiraMadeira_KES_absoluta = False, PP_MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao), PP_Magalu_GEA_absoluta = False, PP_Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao), PP_Magalu_KC_absoluta = False, PP_Magalu_KC = float(comiss.CS_Magalu_KC_Comissao), PP_Netshoes_KES_absoluta = False, PP_Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao), PP_Netshoes_ALK_absoluta = False, PP_Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao))
        print(vetor['Codigo'], "cadastrdo")


@login_required
def subir(request):
    usuario = request.user
    setor = request.user.Us_Setor
    if setor == "ti":
        preco = Produto_Precificacao.objects.all()
        comissoes = get_object_or_404(Comissoes, pk='1')
        for n in range(0,len(preco)):
            sku = preco[n]
            


    return render(request, 'precos/todosprecos.html')