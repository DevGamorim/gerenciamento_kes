from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Log_Pedidos, Pedido, Estoque_arrigo,Log_estoques
from produtos.models import Produto
# Create your views here.

#Bibliotecas Externo
import os
import pandas as pd
from openpyxl import Workbook
import pyrebase
import json
import yaml
from collections import OrderedDict
from datetime import datetime
from pygame import mixer
import pygame
from time import sleep


config = {}


firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
db = firebase.database()

def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote



@login_required
def home(request):
    return render(request, 'pages/homepedidos.html')
    #return HttpResponse('Hello World!')

@login_required
def Novo_pedido(request):
    user = request.user
    lista_produs = []
    banco = {
        'PD_identificacao':'',
        'PD_sku1':'',
        'PD_quant1':'',
        'PD_obs1':'',
        'PD_preco1':'',
        'PD_titulo_produto1':'',
        'PD_cor_produto1':'',
        'PD_material_produto1':'',
        'PD_imagem_produto1':'',
        'PD_sku2':'',
        'PD_quant2':'',
        'PD_obs2':'',
        'PD_preco2':'',
        'PD_titulo_produto2':'',
        'PD_cor_produto2':'',
        'PD_material_produto2':'',
        'PD_imagem_produto2':'',
        'PD_sku3':'',
        'PD_quant3':'',
        'PD_obs3':'',
        'PD_preco3':'',
        'PD_titulo_produto3':'',
        'PD_cor_produto3':'',
        'PD_material_produto3':'',
        'PD_imagem_produto3':'',
        'PD_sku4':'',
        'PD_quant4':'',
        'PD_obs4':'',
        'PD_preco4':'',
        'PD_titulo_produto4':'',
        'PD_cor_produto4':'',
        'PD_material_produto4':'',
        'PD_imagem_produto4':'',
        'PD_sku5':'',
        'PD_quant5':'',
        'PD_obs5':'',
        'PD_preco5':'',
        'PD_titulo_produto5':'',
        'PD_cor_produto5':'',
        'PD_material_produto5':'',
        'PD_imagem_produto5':'',
        'PD_sku6':'',
        'PD_quant6':'',
        'PD_obs6':'',
        'PD_preco6':'',
        'PD_titulo_produto6':'',
        'PD_cor_produto6':'',
        'PD_material_produto6':'',
        'PD_imagem_produto6':'',
        'PD_sku7':'',
        'PD_quant7':'',
        'PD_obs7':'',
        'PD_preco7':'',
        'PD_titulo_produto7':'',
        'PD_cor_produto7':'',
        'PD_material_produto7':'',
        'PD_imagem_produto7':'',
        'PD_sku8':'',
        'PD_quant8':'',
        'PD_obs8':'',
        'PD_preco8':'',
        'PD_titulo_produto8':'',
        'PD_cor_produto8':'',
        'PD_material_produto8':'',
        'PD_imagem_produto8':'',
        'PD_sku9':'',
        'PD_quant9':'',
        'PD_obs9':'',
        'PD_preco9':'',
        'PD_titulo_produto9':'',
        'PD_cor_produto9':'',
        'PD_material_produto9':'',
        'PD_imagem_produto9':'',
        'PD_sku10':'',
        'PD_quant10':'',
        'PD_obs10':'',
        'PD_preco10':'',
        'PD_titulo_produto10':'',
        'PD_cor_produto10':'',
        'PD_material_produto10':'',
        'PD_imagem_produto10':'',
        'PD_portal':'',
        'PD_coleta':'',
        'PD_dia_finalizar':'',
        'PD_aviso_novo':False,
        'PD_full':'',
        'user_created':str(user),
        'user_updated':str(user),
        'PD_status': 'Novo',
        'PD_excluido':False,
        'PD_valor_total':'',
        'PD_quant_sku':'',
        'PD_finalizado':False,
        'PD_dia_hora_entrega':'',
    }
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        a = 0
        for key, value in tudo.items():
            lista_produs.append(key)
            
        for n in range(0,len(lista_produs)):
            chave = str(lista_produs[n])
            numero = chave[3:]
            print(chave,chave[3:])
            if tudo[chave] == '':
                if chave[:3] == 'sku':
                    sku = 'PD_sku'+str(chave[3:])
                    banco[sku] = None
                    titulo = 'PD_titulo_produto' +str(chave[3:])
                    banco[titulo] = None
                    imagem = 'PD_imagem_produto' +str(chave[3:])
                    banco[imagem] = None
                    corbanco = 'PD_cor_produto' +str(chave[3:])
                    banco[corbanco] = None
                    material_ = 'PD_material_produto' +str(chave[3:])
                    banco[material_] = None

                if chave[:3] == 'qua':
                    quantidade = 'PD_quant'+str(chave[5:])
                    banco[quantidade] = None
                
                if chave[:3] == 'obs':
                    obs = 'PD_obs'+str(chave[3:])
                    banco[obs] = ""

                if chave[:3] == 'val':
                    preco = 'PD_preco'+str(chave[5:])
                    banco[preco] = None

            else:
                if str(chave[:3]) == 'sku':
                    a = a + 1
                    sku = 'PD_sku'+str(chave[3:])
                    banco[sku] = str(tudo[chave]).upper()
                    tudo[chave] = str(tudo[chave]).upper()

                    prod = Produto.objects.get(Pro_Sku = str(tudo[chave]).upper())
                    titulo = 'PD_titulo_produto' +str(chave[3:])
                    banco[titulo] = prod.Pro_Nome
                    
                    imagem = 'PD_imagem_produto' +str(chave[3:])
                    skuh = str(tudo[chave])
                    link = "http://alaoq.com.br/imagem/finalizada/"+ str(skuh[:2]).upper() + "/"+ str(skuh).upper() + "/" + str(skuh).upper() + "_" + "1.jpg"
                    banco[imagem] = link

                    corbanco = 'PD_cor_produto' +str(chave[3:])
                    
                    material_ = 'PD_material_produto' +str(chave[3:])
                    lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                    cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                    'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                    materiais = ['MDF','mdf','Pinus','pinus']
                    try:
                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue
                    except:
                        corbanco = 'PD_cor_produto' +str(chave[3:])
                        banco[corbanco] = 'Confirmar Cor'
                        material_ = 'PD_material_produto' +str(chave[3:])
                        banco[material_] = 'Confirmar Material'

                try:
                    if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                        cor = 'Branco'
                        banco[corbanco] = cor
                    elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                        cor = 'Preto'
                        banco[corbanco] = cor
                    elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                        cor = 'Amadeirado'
                        banco[corbanco] = cor
                    elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                        cor = 'Ipê'
                        banco[corbanco] = cor
                    elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                        cor = 'Imbuia'
                        banco[corbanco] = cor
                    elif cor == 'Natural envernizado':
                        banco[corbanco] = cor
                    elif cor == 'Natural sem verniz':
                        banco[corbanco] = cor
                    else:
                        cor = 'Confirmar Cor'
                        banco[corbanco] = cor
                except:
                    corbanco = 'PD_cor_produto' +str(chave[3:])
                    banco[corbanco] = 'Confirmar Cor'
                try:
                    if material == 'MDF' or material == 'mdf':
                        material = 'MDF'
                        banco[material_] = material
                    elif material == 'Pinus' or material == 'pinus':
                        material = 'Pinus'
                        banco[material_] = material
                    else:
                        material = 'Confirmar Material'
                        banco[material_] = material
                except:
                    material_ = 'PD_material_produto' +str(chave[3:])
                    banco[material_] = 'Confirmar Material'

                if str(chave[:3]) == 'qua':
                    quantidade = 'PD_quant'+str(chave[5:])
                    try:
                        banco[quantidade] = int(tudo[chave])
                    except:
                        print("aviso sem estoque")
                
                if str(chave[:3]) == 'obs':
                    obs = 'PD_obs'+str(chave[3:])
                    banco[obs] = tudo[chave]

                if str(chave[:3]) == 'val':
                    preco = 'PD_preco'+str(chave[5:])
                    valor = str(tudo[chave]).replace("R$","")
                    valor = valor.replace(" ","")
                    valor = valor.replace(",",".")
                    valor = float(valor)
                    banco[preco] = valor
        
                if str(chave[:3]) == 'por':
                    banco['PD_portal'] = str(tudo[chave])

                if str(chave[:3]) == 'ped':
                    banco['PD_identificacao'] = str(tudo[chave])

                if str(chave[:3]) == 'pri':
                    hora = str(tudo[chave])
                    hora = hora.replace("0:00","0")
                    hora = hora.replace("0:0","0")
                    if hora == "FULL":
                        hora = "17:30"
                        tudo['prioridade'] = "17:30"
                        banco['PD_full'] = True
                    else:
                        banco['PD_full'] = False

                    banco['PD_coleta'] = hora
                if str(chave[:3]) == 'dat':
                    hora = str(tudo[chave])
                    hora = str(hora).split("-")
                    try:
                        hora = str(hora[2])+"/"+str(hora[1])+"/"+str(hora[0])
                    except:
                        banco['PD_dia_finalizar'] = str(tudo[chave])
                    banco['PD_dia_finalizar'] = hora

                try:
                    hora = tudo['data']
                    hora = str(hora).split("-")
                    hora = str(hora[2])+"/"+str(hora[1])+"/"+str(hora[0])
                    hora = str(hora)+" "+str(tudo['prioridade'])+"0"
                    hora = hora.replace("-","/")
                    hora = datetime.strptime(str(hora), '%d/%m/%Y %H:%M:%S')
                    print("ok",hora)
                except:
                    hora = datetime.today()
                    print("erro",hora)

        
        banco['PD_dia_hora_entrega'] = hora
        valor_total = float(0)
        for n in range(1,11):
            if n == 11:
                n = n - 1
                break
            else:
                tag = 'PD_preco'+str(n)
                quantidade = 'PD_quant'+str(n)
                try:
                    quantidade = int(banco[quantidade])
                except:                    
                    break
                valor = 0
                valor = banco[tag]*quantidade
                valor_total = valor + valor_total
        banco['PD_quant_sku'] = a
        if a == 0:
            return render(request, 'pedidos/novo.html')
        else:
            banco['PD_valor_total'] = valor_total
            print('valor_total',valor_total,'\nPD_quant_sku',banco['PD_quant_sku'])
            print(banco)
            pedido = Pedido.objects.create(PD_dia_hora_entrega=banco['PD_dia_hora_entrega'],PD_finalizado=banco['PD_finalizado'],PD_quant_sku=banco['PD_quant_sku'],PD_valor_total=banco['PD_valor_total'],PD_status = banco['PD_status'], PD_excluido = banco['PD_excluido'],PD_identificacao = banco['PD_identificacao'], PD_sku1 = banco['PD_sku1'], PD_quant1 = banco['PD_quant1'], PD_obs1 = banco['PD_obs1'], PD_preco1 = banco['PD_preco1'], PD_titulo_produto1 = banco['PD_titulo_produto1'], PD_cor_produto1 = banco['PD_cor_produto1'], PD_material_produto1 = banco['PD_material_produto1'], PD_imagem_produto1 = banco['PD_imagem_produto1'], PD_sku2 = banco['PD_sku2'], PD_quant2 = banco['PD_quant2'], PD_obs2 = banco['PD_obs2'], PD_preco2 = banco['PD_preco2'], PD_titulo_produto2 = banco['PD_titulo_produto2'], PD_cor_produto2 = banco['PD_cor_produto2'], PD_material_produto2 = banco['PD_material_produto2'], PD_imagem_produto2 = banco['PD_imagem_produto2'], PD_sku3 = banco['PD_sku3'], PD_quant3 = banco['PD_quant3'], PD_obs3 = banco['PD_obs3'], PD_preco3 = banco['PD_preco3'], PD_titulo_produto3 = banco['PD_titulo_produto3'], PD_cor_produto3 = banco['PD_cor_produto3'], PD_material_produto3 = banco['PD_material_produto3'], PD_imagem_produto3 = banco['PD_imagem_produto3'], PD_sku4 = banco['PD_sku4'], PD_quant4 = banco['PD_quant4'], PD_obs4 = banco['PD_obs4'], PD_preco4 = banco['PD_preco4'], PD_titulo_produto4 = banco['PD_titulo_produto4'], PD_cor_produto4 = banco['PD_cor_produto4'], PD_material_produto4 = banco['PD_material_produto4'], PD_imagem_produto4 = banco['PD_imagem_produto4'], PD_sku5 = banco['PD_sku5'], PD_quant5 = banco['PD_quant5'], PD_obs5 = banco['PD_obs5'], PD_preco5 = banco['PD_preco5'], PD_titulo_produto5 = banco['PD_titulo_produto5'], PD_cor_produto5 = banco['PD_cor_produto5'], PD_material_produto5 = banco['PD_material_produto5'], PD_imagem_produto5 = banco['PD_imagem_produto5'], PD_sku6 = banco['PD_sku6'], PD_quant6 = banco['PD_quant6'], PD_obs6 = banco['PD_obs6'], PD_preco6 = banco['PD_preco6'], PD_titulo_produto6 = banco['PD_titulo_produto6'], PD_cor_produto6 = banco['PD_cor_produto6'], PD_material_produto6 = banco['PD_material_produto6'], PD_imagem_produto6 = banco['PD_imagem_produto6'], PD_sku7 = banco['PD_sku7'], PD_quant7 = banco['PD_quant7'], PD_obs7 = banco['PD_obs7'], PD_preco7 = banco['PD_preco7'], PD_titulo_produto7 = banco['PD_titulo_produto7'], PD_cor_produto7 = banco['PD_cor_produto7'], PD_material_produto7 = banco['PD_material_produto7'], PD_imagem_produto7 = banco['PD_imagem_produto7'], PD_sku8 = banco['PD_sku8'], PD_quant8 = banco['PD_quant8'], PD_obs8 = banco['PD_obs8'], PD_preco8 = banco['PD_preco8'], PD_titulo_produto8 = banco['PD_titulo_produto8'], PD_cor_produto8 = banco['PD_cor_produto8'], PD_material_produto8 = banco['PD_material_produto8'], PD_imagem_produto8 = banco['PD_imagem_produto8'], PD_sku9 = banco['PD_sku9'], PD_quant9 = banco['PD_quant9'], PD_obs9 = banco['PD_obs9'], PD_preco9 = banco['PD_preco9'], PD_titulo_produto9 = banco['PD_titulo_produto9'], PD_cor_produto9 = banco['PD_cor_produto9'], PD_material_produto9 = banco['PD_material_produto9'], PD_imagem_produto9 = banco['PD_imagem_produto9'], PD_sku10 = banco['PD_sku10'], PD_quant10 = banco['PD_quant10'], PD_obs10 = banco['PD_obs10'], PD_preco10 = banco['PD_preco10'], PD_titulo_produto10 = banco['PD_titulo_produto10'], PD_cor_produto10 = banco['PD_cor_produto10'], PD_material_produto10 = banco['PD_material_produto10'], PD_imagem_produto10 = banco['PD_imagem_produto10'], PD_portal = banco['PD_portal'], PD_coleta = banco['PD_coleta'], PD_dia_finalizar = banco['PD_dia_finalizar'], PD_aviso_novo = banco['PD_aviso_novo'], PD_full = banco['PD_full'], user_created = banco['user_created'], user_updated = banco['user_updated'])
    return render(request, 'pedidos/novo.html')


@login_required
def historico(request):
    pedidos = Pedido.objects.filter(PD_finalizado=False).order_by("PD_dia_finalizar")
    return render(request, 'pedidos/historico.html',{"lista_skus":pedidos})
    ###print('producao_aviso')


@login_required
def producao(request):
    user = request.user
    setor = request.user.Us_Setor
    alarme = ''
    lista_master = {}
    retorno = []
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = str(tudo).replace("<QueryDict:","").upper()
        tudo = tudo.replace(">","")
        tudo =  yaml.safe_load(tudo)
        print(tudo)
        pedidos_post = tudo['AVANCAR']
        
        for n in range(0,len(pedidos_post)):
            pedido = Pedido.objects.get(PD_ID=pedidos_post[n])
            if pedido.PD_status == "Novo":
                pedido.PD_status = "Em produção"
                pedido.save()
            elif pedido.PD_status == "Em produção":
                pedido.PD_status = "Pronto"
                pedido.save()
            elif pedido.PD_status == "Pronto":
                if setor == 'producao':
                    continue
                else:
                    pedido.PD_status = "Concluido"
                    pedido.PD_finalizado = True
                    pedido.save()
                
        pedidos = Pedido.objects.filter(PD_finalizado=False).order_by("PD_dia_finalizar")
        for n in range(0,len(pedidos)):
            aviso = pedidos[n]
            print(aviso.PD_aviso_novo)
            try:
                #print(dict_pedido['aviso'],dict_pedido['Pedido'])
                if aviso.PD_aviso_novo == False:
                    aviso.PD_aviso_novo = True
                    aviso.save()
                    pygame.init()
                    mixer.init()
                    filepath = os.path.abspath(__file__)
                    filedir = os.path.dirname(filepath)
                    for n in (0,2):
                        musicpath = os.path.join(filedir, "som.wav")
                        mixer.music.load(musicpath) # Music file can only be MP3
                        mixer.music.play()
                        while True:
                            sleep(4)
                            break
                    status = {"aviso":"ok"}
                    try:
                        aviso.PD_aviso_novo = True
                        aviso.save()
                        print("pedido salvo",aviso.PD_aviso_novo)
                    except:
                        aviso.PD_aviso_novo = True
                        aviso.save()
                        print("pedido salvo",aviso.PD_aviso_novo)
                    #print(dict_pedido['Pedido'],' audio emitido')
                else:
                    a = ''
                    #print(dict_pedido['Pedido'],' sem aduio')
            except:
                a = ''
        return render(request, 'pedidos/producao.html',{"lista_skus":pedidos,'alarme':alarme})


    else:

        pedidos = Pedido.objects.filter(PD_finalizado=False).order_by("PD_dia_finalizar")
        for n in range(0,len(pedidos)):
            aviso = pedidos[n]
            print(aviso.PD_aviso_novo)
            try:
                #print(dict_pedido['aviso'],dict_pedido['Pedido'])
                if setor == 'producao':
                    if aviso.PD_aviso_novo == False:
                        aviso.PD_aviso_novo = True
                        aviso.save()
                        pygame.init()
                        mixer.init()
                        filepath = os.path.abspath(__file__)
                        filedir = os.path.dirname(filepath)
                        for n in (0,2):
                            musicpath = os.path.join(filedir, "som.wav")
                            mixer.music.load(musicpath) # Music file can only be MP3
                            mixer.music.play()
                            while True:
                                sleep(4)
                                break
                        status = {"aviso":"ok"}
                        try:
                            aviso.PD_aviso_novo = True
                            aviso.save()
                            print("pedido salvo",aviso.PD_aviso_novo)
                        except:
                            aviso.PD_aviso_novo = True
                            aviso.save()
                            print("pedido salvo",aviso.PD_aviso_novo)
                        #print(dict_pedido['Pedido'],' audio emitido')
                    else:
                        a = ''
                        #print(dict_pedido['Pedido'],' sem aduio')
            except:
                a = ''
        return render(request, 'pedidos/producao.html',{"lista_skus":pedidos,'alarme':alarme})


@login_required
def pedidos(request):
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)
        pedido = Pedido.objects.filter(PD_identificacao=tudo['pedidos'])
    else:
        pedido = Pedido.objects.all().order_by('PD_dia_hora_entrega')
    return render(request, 'pedidos/pedidos.html',{"lista_skus":pedido})
    

@login_required
def relatorio(request):
    setor = request.user.Us_Setor
    if setor == 'administracao' or setor == 'ti':
        if request.method == 'POST':
            tudo = request.POST.copy()
            tudo = json.dumps(tudo)
            tudo = json.loads(tudo)
            print(tudo)

            pedidos = ''

            data = str(tudo['data']).replace("-","/")
            data = str(data).split(" / ")
            data[0] = datetime.strptime(str(data[0]), '%d/%m/%Y')
            data[1] = datetime.strptime(str(data[1]), '%d/%m/%Y')

            if data[0] == data[1]:
                print('igual')
            elif data[0] != data[1]:
                print('diferente')


            portal = tudo['portal']
            
            pedido = tudo['pedido']

            full = tudo['full']
            print(len(pedido))
            if len(pedido) >= 1:
                print("so pedido")
                pedidos = Pedido.objects.filter(PD_excluido=False, PD_identificacao=pedido).order_by('PD_dia_hora_entrega')

            #com data portal e full            
            elif data[0] != data[1] and len(portal) >= 2 and len(full) >= 2:
                print(full)
                if full == "sim":
                    print("dias com portal so full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1],PD_portal=portal, PD_full=True).order_by('PD_dia_hora_entrega')
                else:
                    print("dias com portal sem full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1],PD_portal=portal, PD_full=False).order_by('PD_dia_hora_entrega')
            
            #sem data, com portal e full
            elif data[0] == data[1] and len(portal) >= 2 and len(full) >= 2:
                if full == "sim":
                    print("portal so full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_portal=portal, PD_full=True).order_by('PD_dia_hora_entrega')
                else:
                    print("portal sem full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_portal=portal, PD_full=False).order_by('PD_dia_hora_entrega')
            
            #com data e portal sem full
            elif data[0] != data[1] and len(portal) >= 2 and len(full) <= 2:
                pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1],PD_portal=portal).order_by('PD_dia_hora_entrega')
            
            #com data e full sem portal
            elif data[0] != data[1] and len(portal) <= 2 and len(full) >= 2:
                if full == "sim":
                    print("dias so full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1], PD_full=True).order_by('PD_dia_hora_entrega')
                else:
                    print("dias sem full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1], PD_full=False).order_by('PD_dia_hora_entrega')
            
            #com data sem portal e sem full
            elif data[0] != data[1] and len(portal) <= 2 and len(full) <= 2:
                print("so dias")
                pedidos = Pedido.objects.filter(PD_excluido=False, PD_dia_hora_entrega__gte=data[0],PD_dia_hora_entrega__lte=data[1]).order_by('PD_dia_hora_entrega')

            #sem data sem portal, so full
            elif data[0] == data[1] and len(portal) <= 2 and len(full) >= 2:
                if full == "sim":
                    print("tudo so full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_full=True).order_by('PD_dia_hora_entrega')
                else:
                    print("tudo sem full")
                    pedidos = Pedido.objects.filter(PD_excluido=False, PD_full=False).order_by('PD_dia_hora_entrega')
            
            #sem data com portal sem full
            elif data[0] == data[1] and len(portal) >= 2 and len(full) <= 2:
                print("So portal")
                pedidos = Pedido.objects.filter(PD_excluido=False, PD_portal=portal).order_by('PD_dia_hora_entrega')


            #todos
            else:
                print("todos")
                pedidos = Pedido.objects.filter(PD_excluido=False).order_by('PD_dia_hora_entrega')

            
            
            valot_total_relatorio = "teste"
            ticke_medio = "teste"
            retorno = ['1']
        else:
            pedidos = Pedido.objects.filter(PD_excluido=False).order_by('PD_dia_hora_entrega')

        valot_total_relatorio = 0
        ticke_medio = 0
        if len(pedidos) == 0:
            valot_total_relatorio = "Sem pedidos"
            ticke_medio = "Sem pedidos"
        else:
            for n in range(0,len(pedidos)):
                valot_total_relatorio = pedidos[n].PD_valor_total + valot_total_relatorio

            ticke_medio = valot_total_relatorio/len(pedidos)
        return render(request, 'pedidos/Relatorio.html',{"lista_skus":pedidos,"valor_total":valot_total_relatorio,"ticket_medio": ticke_medio,'quant_pedidos':len(pedidos)})
    else:
        return render(request,'Erro_AcessoNegado.html')

@login_required
def editar(request):
    setor = request.user.Us_Setor
    pedidos = ''
    tipo = ''
    if setor == 'administracao' or setor == 'ti' or setor == 'comercial' or setor == 'logistica':
        if request.method == 'POST':
            tudo = request.POST.copy()
            tudo = json.dumps(tudo)
            tudo = json.loads(tudo)
            print(tudo)

            try:
                id_ = tudo['cancelar-pedido']
                pedidobuscar = "exluir"
            except:
                try:
                    pedidobuscar = tudo['pedidobuscar']
                except:
                    pedidobuscar = "editar"

            if pedidobuscar == "exluir":
                pedido = Pedido.objects.get(pk=id_)
                pedido.PD_excluido = True
                pedido.save()
            
            if pedidobuscar != "editar":
                try:
                    pedidos = Pedido.objects.filter(PD_identificacao=str(tudo['pedidobuscar']))
                    pedido = Pedido.objects.get(PD_identificacao=str(tudo['pedidobuscar']))
                except:
                    return render(request, 'pedidos/Editar.html')
                print("aaaa")
                tipo = 'Editar'
                return render(request, 'pedidos/Editar.html',{"sku":pedido,"tipo":tipo,"pedido":pedido.PD_ID,"nome_pedido":pedido.PD_identificacao})
            
            
            elif pedidobuscar == "editar":
                pedido = Pedido.objects.get(PD_identificacao=str(tudo['pedido']))
                if len(tudo['status']) >= 1:
                    if pedido.PD_status != tudo['status']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_status",LP_novo_valor=tudo['status'],LP_antigo_valor=pedido.PD_status,LP_user=str(request.user))
                        pedido.PD_status = tudo['status']
                        
                        if tudo['status'] == "Concluido":
                            pedido.PD_finalizado = True
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_finalizado",LP_novo_valor="True",LP_antigo_valor="False",LP_user=str(request.user))

                if len(tudo['portal']) >= 1:
                    if pedido.PD_portal != tudo['portal']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_portal", LP_antigo_valor=pedido.PD_portal,LP_novo_valor=tudo['portal'],LP_user=str(request.user))
                        pedido.PD_portal = tudo['portal']

                if len(tudo['hora']) >= 1:
                    if pedido.PD_coleta != tudo['hora']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_coleta", LP_antigo_valor=pedido.PD_coleta,LP_novo_valor=tudo['hora'],LP_user=str(request.user))
                        pedido.PD_coleta = tudo['hora']
                        if tudo['hora'] == "FULL":
                            tudo['hora'] = "17:30:0"
                        hora = tudo['data']
                        hora = str(hora).split("-")
                        hora = str(hora[2])+"/"+str(hora[1])+"/"+str(hora[0])
                        hora = str(hora)+" "+str(tudo['hora'])+"0"
                        hora = str(hora).replace("300","30:00")
                        hora = str(hora).replace("000","00:00")
                        hora = hora.replace("-","/")
                        hora = datetime.strptime(str(hora), '%d/%m/%Y %H:%M:%S')
                        pedido.PD_dia_hora_entrega = hora
                    
                
                if len(tudo['data']) >= 1:
                    if pedido.PD_dia_finalizar != tudo['data']:
                        hora = tudo['data']
                        hora = str(hora).split("-")
                        hora = str(hora[2])+"/"+str(hora[1])+"/"+str(hora[0])
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_dia_finalizar", LP_antigo_valor=pedido.PD_dia_finalizar,LP_novo_valor=hora,LP_user=str(request.user))
                        pedido.PD_dia_finalizar = hora
                        if tudo['hora'] == "FULL":
                            tudo['hora'] = "17:30:0"
                        hora = tudo['data']
                        hora = str(hora).split("-")
                        hora = str(hora[2])+"/"+str(hora[1])+"/"+str(hora[0])
                        hora = str(hora)+" "+str(tudo['hora'])+"0"
                        hora = str(hora).replace("300","30:00")
                        hora = str(hora).replace("000","00:00")
                        hora = hora.replace("-","/")
                        hora = datetime.strptime(str(hora), '%d/%m/%Y %H:%M:%S')
                        pedido.PD_dia_hora_entrega = hora

                if len(tudo['hora']) >= 1 or len(tudo['data']) >= 1:
                    if tudo['hora'] == "FULL":
                        if pedido.PD_full != True:
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_full", LP_antigo_valor=pedido.PD_full,LP_novo_valor="True",LP_user=str(request.user))
                            pedido.PD_full = True
                
                a = 1
                if len(tudo['sku1']) >= 1:
                    if pedido.PD_sku1 != tudo['sku1']:
                        sku = tudo['sku1']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku1", LP_antigo_valor=pedido.PD_sku1,LP_novo_valor=sku,LP_user=str(request.user))
                        pedido.PD_sku1 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto1", LP_antigo_valor=pedido.PD_titulo_produto1,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        pedido.PD_titulo_produto1 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto1", LP_antigo_valor=pedido.PD_imagem_produto1,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto1 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                            
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        elif cor == 'Natural envernizado':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto1", LP_antigo_valor=pedido.PD_cor_produto1,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto1 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_material_produto1", LP_antigo_valor=pedido.PD_material_produto1,LP_novo_valor=material,LP_user=str(request.user))
                            pedido.PD_material_produto1 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_material_produto1", LP_antigo_valor=pedido.PD_material_produto1,LP_novo_valor=material,LP_user=str(request.user))
                            pedido.PD_material_produto1 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_material_produto1", LP_antigo_valor=pedido.PD_material_produto1,LP_novo_valor=material,LP_user=str(request.user))
                            pedido.PD_material_produto1 = material
                if len(tudo['quant1']) >= 1:    
                    if pedido.PD_quant1 != tudo['quant1']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant1", LP_antigo_valor=pedido.PD_quant1,LP_novo_valor=tudo['quant1'],LP_user=str(request.user))
                        pedido.PD_quant1 = tudo['quant1']
                if len(tudo['obs1']) >= 1:     
                    if pedido.PD_obs1 != tudo['obs1']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs1", LP_antigo_valor=pedido.PD_obs1,LP_novo_valor=tudo['obs1'],LP_user=str(request.user))
                        pedido.PD_obs1 = tudo['obs1']
                if len(tudo['valor1']) >= 1:
                    valor = str(tudo['valor1']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    if pedido.PD_preco1 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco1", LP_antigo_valor=pedido.PD_preco1,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco1 != valor
                
                
                if pedido.PD_sku2 != None:
                    a = a + 1
                if len(tudo['sku2']) >= 1:
                    if pedido.PD_sku2 != tudo['sku2']:
                        a = a + 1
                        sku = tudo['sku2']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku2", LP_antigo_valor=pedido.PD_sku2,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku2 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto2", LP_antigo_valor=pedido.PD_titulo_produto2,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto2 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto2", LP_antigo_valor=pedido.PD_imagem_produto2,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto2 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto2 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto2 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto2 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto2 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto2", LP_antigo_valor=pedido.PD_cor_produto2,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto2 = material
                if len(tudo['quant2']) >= 1:
                    if pedido.PD_quant2 != tudo['quant2']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant2", LP_antigo_valor=pedido.PD_quant2,LP_novo_valor=tudo['quant2'],LP_user=str(request.user))

                        pedido.PD_quant2 = tudo['quant2']
                if len(tudo['obs2']) >= 1:
                    if pedido.PD_obs2 != tudo['obs2']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs2", LP_antigo_valor=pedido.PD_obs2,LP_novo_valor=tudo['obs2'],LP_user=str(request.user))
                        pedido.PD_obs2 = tudo['obs2']
                if len(tudo['valor2']) >= 1:
                    valor = str(tudo['valor2']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco2 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco2", LP_antigo_valor=pedido.PD_preco2,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco2 = valor

                if pedido.PD_sku3 != None:
                    a = a + 1
                if len(tudo['sku3']) >= 1:
                    if pedido.PD_sku3 != tudo['sku3']:
                        a = a + 1
                        sku = tudo['sku3']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku3", LP_antigo_valor=pedido.PD_sku3,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku3 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto3", LP_antigo_valor=pedido.PD_titulo_produto3,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto3 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto3", LP_antigo_valor=pedido.PD_imagem_produto3,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto3 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto3 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto3 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto3 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto3 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto3", LP_antigo_valor=pedido.PD_cor_produto3,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto3 = material
                if len(tudo['quant3']) >= 1:
                    if pedido.PD_quant3 != tudo['quant3']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant3", LP_antigo_valor=pedido.PD_quant3,LP_novo_valor=tudo['quant3'],LP_user=str(request.user))

                        pedido.PD_quant3 = tudo['quant3']
                if len(tudo['obs3']) >= 1:
                    if pedido.PD_obs3 != tudo['obs3']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs3", LP_antigo_valor=pedido.PD_obs3,LP_novo_valor=tudo['obs3'],LP_user=str(request.user))
                        pedido.PD_obs3 = tudo['obs3']
                if len(tudo['valor3']) >= 1:
                    valor = str(tudo['valor3']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco3 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco3", LP_antigo_valor=pedido.PD_preco3,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco3 = valor

                if pedido.PD_sku4 != None:
                    a = a + 1
                if len(tudo['sku4']) >= 1:
                    if pedido.PD_sku4 != tudo['sku4']:
                        a = a + 1
                        sku = tudo['sku4']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku4", LP_antigo_valor=pedido.PD_sku4,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku4 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto4", LP_antigo_valor=pedido.PD_titulo_produto4,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto4 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto4", LP_antigo_valor=pedido.PD_imagem_produto4,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto4 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto4 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto4 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto4 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto4 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto4", LP_antigo_valor=pedido.PD_cor_produto4,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto4 = material
                if len(tudo['quant4']) >= 1:
                    if pedido.PD_quant4 != tudo['quant4']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant4", LP_antigo_valor=pedido.PD_quant4,LP_novo_valor=tudo['quant4'],LP_user=str(request.user))

                        pedido.PD_quant4 = tudo['quant4']
                if len(tudo['obs4']) >= 1:
                    if pedido.PD_obs4 != tudo['obs4']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs4", LP_antigo_valor=pedido.PD_obs4,LP_novo_valor=tudo['obs4'],LP_user=str(request.user))
                        pedido.PD_obs4 = tudo['obs4']
                if len(tudo['valor4']) >= 1:
                    valor = str(tudo['valor4']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco4 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco4", LP_antigo_valor=pedido.PD_preco4,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco4 = valor

                if pedido.PD_sku5 != None:
                    a = a + 1
                if len(tudo['sku5']) >= 1:
                    if pedido.PD_sku5 != tudo['sku5']:
                        a = a + 1
                        sku = tudo['sku5']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku5", LP_antigo_valor=pedido.PD_sku5,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku5 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto5", LP_antigo_valor=pedido.PD_titulo_produto5,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto5 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto5", LP_antigo_valor=pedido.PD_imagem_produto5,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto5 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto5 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto5 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto5 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto5 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto5", LP_antigo_valor=pedido.PD_cor_produto5,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto5 = material
                if len(tudo['quant5']) >= 1:
                    if pedido.PD_quant5 != tudo['quant5']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant5", LP_antigo_valor=pedido.PD_quant5,LP_novo_valor=tudo['quant5'],LP_user=str(request.user))

                        pedido.PD_quant5 = tudo['quant5']
                if len(tudo['obs5']) >= 1:
                    if pedido.PD_obs5 != tudo['obs5']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs5", LP_antigo_valor=pedido.PD_obs5,LP_novo_valor=tudo['obs5'],LP_user=str(request.user))
                        pedido.PD_obs5 = tudo['obs5']
                if len(tudo['valor5']) >= 1:
                    valor = str(tudo['valor5']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco5 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco5", LP_antigo_valor=pedido.PD_preco5,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco5 = valor

                if pedido.PD_sku6 != None:
                    a = a + 1
                if len(tudo['sku6']) >= 1:
                    if pedido.PD_sku6 != tudo['sku6']:
                        a = a + 1
                        sku = tudo['sku6']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku6", LP_antigo_valor=pedido.PD_sku6,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku6 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto6", LP_antigo_valor=pedido.PD_titulo_produto6,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto6 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto6", LP_antigo_valor=pedido.PD_imagem_produto6,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto6 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto6 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto6 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto6 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto6 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto6", LP_antigo_valor=pedido.PD_cor_produto6,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto6 = material
                if len(tudo['quant6']) >= 1:
                    if pedido.PD_quant6 != tudo['quant6']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant6", LP_antigo_valor=pedido.PD_quant6,LP_novo_valor=tudo['quant6'],LP_user=str(request.user))

                        pedido.PD_quant6 = tudo['quant6']
                if len(tudo['obs6']) >= 1:
                    if pedido.PD_obs6 != tudo['obs6']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs6", LP_antigo_valor=pedido.PD_obs6,LP_novo_valor=tudo['obs6'],LP_user=str(request.user))
                        pedido.PD_obs6 = tudo['obs6']
                if len(tudo['valor6']) >= 1:
                    valor = str(tudo['valor6']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco6 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco6", LP_antigo_valor=pedido.PD_preco6,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco6 = valor

                if pedido.PD_sku7 != None:
                    a = a + 1
                if len(tudo['sku7']) >= 1:
                    if pedido.PD_sku7 != tudo['sku7']:
                        a = a + 1
                        sku = tudo['sku7']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku7", LP_antigo_valor=pedido.PD_sku7,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku7 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto7", LP_antigo_valor=pedido.PD_titulo_produto7,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto7 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto7", LP_antigo_valor=pedido.PD_imagem_produto7,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto7 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto7 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto7 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto7 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto7 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto7", LP_antigo_valor=pedido.PD_cor_produto7,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto7 = material
                if len(tudo['quant7']) >= 1:
                    if pedido.PD_quant7 != tudo['quant7']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant7", LP_antigo_valor=pedido.PD_quant7,LP_novo_valor=tudo['quant7'],LP_user=str(request.user))

                        pedido.PD_quant7 = tudo['quant7']
                if len(tudo['obs7']) >= 1:
                    if pedido.PD_obs7 != tudo['obs7']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs7", LP_antigo_valor=pedido.PD_obs7,LP_novo_valor=tudo['obs7'],LP_user=str(request.user))
                        pedido.PD_obs7 = tudo['obs7']
                if len(tudo['valor7']) >= 1:
                    valor = str(tudo['valor7']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco7 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco7", LP_antigo_valor=pedido.PD_preco7,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco7 = valor

                if pedido.PD_sku8 != None:
                    a = a + 1
                if len(tudo['sku8']) >= 1:
                    if pedido.PD_sku8 != tudo['sku8']:
                        a = a + 1
                        sku = tudo['sku8']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku8", LP_antigo_valor=pedido.PD_sku8,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku8 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto8", LP_antigo_valor=pedido.PD_titulo_produto8,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto8 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto8", LP_antigo_valor=pedido.PD_imagem_produto8,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto8 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto8 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto8 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto8 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto8 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto8", LP_antigo_valor=pedido.PD_cor_produto8,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto8 = material
                if len(tudo['quant8']) >= 1:
                    if pedido.PD_quant8 != tudo['quant8']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant8", LP_antigo_valor=pedido.PD_quant8,LP_novo_valor=tudo['quant8'],LP_user=str(request.user))

                        pedido.PD_quant8 = tudo['quant8']
                if len(tudo['obs8']) >= 1:
                    if pedido.PD_obs8 != tudo['obs8']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs8", LP_antigo_valor=pedido.PD_obs8,LP_novo_valor=tudo['obs8'],LP_user=str(request.user))
                        pedido.PD_obs8 = tudo['obs8']
                if len(tudo['valor8']) >= 1:
                    valor = str(tudo['valor8']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco8 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco8", LP_antigo_valor=pedido.PD_preco8,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco8 = valor

                if pedido.PD_sku9 != None:
                    a = a + 1
                if len(tudo['sku9']) >= 1:
                    if pedido.PD_sku9 != tudo['sku9']:
                        a = a + 1
                        sku = tudo['sku9']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku9", LP_antigo_valor=pedido.PD_sku9,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku9 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto9", LP_antigo_valor=pedido.PD_titulo_produto9,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto9 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto9", LP_antigo_valor=pedido.PD_imagem_produto9,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto9 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto9 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto9 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto9 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto9 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto9", LP_antigo_valor=pedido.PD_cor_produto9,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto9 = material
                if len(tudo['quant9']) >= 1:
                    if pedido.PD_quant9 != tudo['quant9']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant9", LP_antigo_valor=pedido.PD_quant9,LP_novo_valor=tudo['quant9'],LP_user=str(request.user))

                        pedido.PD_quant9 = tudo['quant9']
                if len(tudo['obs9']) >= 1:
                    if pedido.PD_obs9 != tudo['obs9']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs9", LP_antigo_valor=pedido.PD_obs9,LP_novo_valor=tudo['obs9'],LP_user=str(request.user))
                        pedido.PD_obs9 = tudo['obs9']
                if len(tudo['valor9']) >= 1:
                    valor = str(tudo['valor9']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco9 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco9", LP_antigo_valor=pedido.PD_preco9,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco9 = valor

                if pedido.PD_sku10 != None:
                    a = a + 1
                if len(tudo['sku10']) >= 1:
                    if pedido.PD_sku10 != tudo['sku10']:
                        a = a + 1
                        sku = tudo['sku10']
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_sku10", LP_antigo_valor=pedido.PD_sku10,LP_novo_valor=valor,LP_user=str(request.user))
                        
                        pedido.PD_sku10 = str(sku).upper()
                        prod = Produto.objects.get(Pro_Sku = str(sku).upper())
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_titulo_produto10", LP_antigo_valor=pedido.PD_titulo_produto10,LP_novo_valor=prod.Pro_Nome,LP_user=str(request.user))
                        
                        pedido.PD_titulo_produto10 = prod.Pro_Nome

                        link = "http://alaoq.com.br/imagem/finalizada/"+ str(sku[:2]).upper() + "/"+ str(sku).upper() + "/" + str(sku).upper() + "_" + "1.jpg"
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_imagem_produto10", LP_antigo_valor=pedido.PD_imagem_produto10,LP_novo_valor=link,LP_user=str(request.user))
                        pedido.PD_imagem_produto10 = link
                        lista_cor_tipo = str(prod.Pro_Nome).split(" ")
                        cores = ['Branco','branco','Branca','branca','Preto','Pretos','Preta','Pretas','preto','pretos','preta','pretas','Amadeirado','amadeirado','madeirado','Madeirado','Natural','natural',
                        'Ipê','ipe','Ipe','ipe','ipê','Imbuia','imbuia','inbuia','Inbuia','Natual','natural']

                        materiais = ['MDF','mdf','Pinus','pinus']

                        for g in range(0,len(lista_cor_tipo)):

                            for gg in range(0,len(cores)):
                                if cores[gg] == lista_cor_tipo[g]:
                                    cor = cores[gg]
                                    if cor == 'Natural' or cor == 'natural':
                                        for hh in range(0,len(lista_cor_tipo)):
                                            if lista_cor_tipo[hh] == 'Verniz' or lista_cor_tipo[hh] == 'verniz':
                                                cor = 'Natural envernizado'
                                                break
                                            else:
                                                cor = 'Natural sem verniz'
                                    gg = 0
                                    break
                                else:
                                    continue
                            for gg in range(0,len(materiais)):
                                if materiais[gg] == lista_cor_tipo[g]:
                                    material = materiais[gg]
                                    break
                                else:
                                    continue


                        if cor == 'Branco' or cor == 'branco' or cor == 'Branca' or cor == 'branca':
                            cor = 'Branco'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Preto' or cor == 'Preta' or cor == 'preto' or cor == 'preta' or cor == 'Pretos' or cor == 'Pretas' or cor == 'pretos' or cor == 'pretas':
                            cor = 'Preto'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Amadeirado' or cor == 'amadeirado' or cor == 'Madeirado' or cor == 'madeirado':
                            cor = 'Amadeirado'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Ipê' or cor == 'ipe' or cor == 'Ipe' or cor == 'ipe' or cor == 'ipê':
                            cor = 'Ipê'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Imbuia' or cor == 'imbuia' or cor =='inbuia' or cor == 'Inbuia':
                            cor = 'Imbuia'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Natural envernizado':
                            pedido.PD_cor_produto10 = cor
                        elif cor == 'Natural sem verniz':
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor
                        else:
                            cor = 'Confirmar Cor'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_cor_produto10 = cor

                        if material == 'MDF' or material == 'mdf':
                            material = 'MDF'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto10 = material
                        elif material == 'Pinus' or material == 'pinus':
                            material = 'Pinus'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto10 = material
                        else:
                            material = 'Confirmar Material'
                            log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_cor_produto10", LP_antigo_valor=pedido.PD_cor_produto10,LP_novo_valor=cor,LP_user=str(request.user))
                            pedido.PD_material_produto10 = material
                if len(tudo['quant10']) >= 1:
                    if pedido.PD_quant10 != tudo['quant10']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_quant10", LP_antigo_valor=pedido.PD_quant10,LP_novo_valor=tudo['quant10'],LP_user=str(request.user))

                        pedido.PD_quant10 = tudo['quant10']
                if len(tudo['obs10']) >= 1:
                    if pedido.PD_obs10 != tudo['obs10']:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_obs10", LP_antigo_valor=pedido.PD_obs10,LP_novo_valor=tudo['obs10'],LP_user=str(request.user))
                        pedido.PD_obs10 = tudo['obs10']
                if len(tudo['valor10']) >= 1:
                    valor = str(tudo['valor10']).replace("R$","")
                    valor = str(valor).replace(" ","")
                    valor = str(valor).replace(",",".")
                    valor = float(valor)
                    print(valor)
                    if pedido.PD_preco10 != valor:
                        log = Log_Pedidos.objects.create(LP_Pedido=pedido, LP_campo="PD_preco10", LP_antigo_valor=pedido.PD_preco10,LP_novo_valor=valor,LP_user=str(request.user))
                        pedido.PD_preco10 = valor

                pedido.PD_quant_sku = a
                pedido.save()
    
    
    return render(request, 'pedidos/Editar.html')


@login_required
def estoque(request):
    retorno = []
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)

        skus = str(tudo['sku1']).replace(", ",",")
        skus = skus.replace(" ",",")
        skus = skus.replace("\n",",")
        skus = skus.replace("\t",",")
        skus = skus.replace(".",",")
        skus = skus.split(",")
        if len(skus[0]) >= 0 or str(skus[0]) != '':
            for n in range(0,len(skus)):
                try:
                    pedido = Estoque_arrigo.objects.get(EA_sku=str(skus[n]))
                    retorno.append(pedido)
                except:
                    retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
                    return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})       
        else:
            retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
    
    else:
        retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
            

    return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})


@login_required
def estoquebaixa(request):

    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)

        sku = tudo['sku1']
        arrigo_novo = tudo['arrigo_novo']
        arrigo_velho = tudo['arrigo_velho']
        koala_novo = tudo['koala_novo']
        koala_velho = tudo['koala_velho']

        estoque =  Estoque_arrigo.objects.get(EA_sku=str(sku))

        if len(str(arrigo_novo)) >= 1:
            arrigo = int(arrigo_velho) - int(arrigo_novo)
            log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_arrigo",LE_novo_valor=arrigo,LE_antigo_valor=estoque.EA_estoque_arrigo,LE_user=str(request.user))
            estoque.EA_estoque_arrigo = arrigo
        else:
            arrigo = arrigo_velho
        if len(str(koala_novo)) >= 1:
            koala = int(koala_velho) - int(koala_novo)
            log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_koala",LE_novo_valor=koala,LE_antigo_valor=estoque.EA_estoque_koala,LE_user=str(request.user))

            estoque.EA_estoque_koala = koala
        else:
            koala = koala_velho

        soma = int(koala) + int(arrigo)

        estoque.EA_estoque_total = str(soma)
        estoque.save()

        retorno = Estoque_arrigo.objects.filter(EA_sku=str(sku)).order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})
    else:
        retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})


@login_required
def estoqueadiciona(request):
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)

        sku = tudo['sku1']
        arrigo_novo = tudo['arrigo_novo']
        arrigo_velho = tudo['arrigo_velho']
        koala_novo = tudo['koala_novo']
        koala_velho = tudo['koala_velho']

        estoque =  Estoque_arrigo.objects.get(EA_sku=str(sku))

        if len(str(arrigo_novo)) >= 1:
            arrigo = int(arrigo_velho) + int(arrigo_novo)
            log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_arrigo",LE_novo_valor=arrigo,LE_antigo_valor=estoque.EA_estoque_arrigo,LE_user=str(request.user))
            estoque.EA_estoque_arrigo = arrigo
        else:
            arrigo = arrigo_velho
        if len(str(koala_novo)) >= 1:
            koala = int(koala_velho) + int(koala_novo)
            log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_koala",LE_novo_valor=koala,LE_antigo_valor=estoque.EA_estoque_koala,LE_user=str(request.user))

            estoque.EA_estoque_koala = koala
        else:
            koala = koala_velho

        soma = int(koala) + int(arrigo)

        estoque.EA_estoque_total = str(soma)
        estoque.save()

        retorno = Estoque_arrigo.objects.filter(EA_sku=str(sku)).order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})
    else:
        retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})


@login_required
def estoqueedit(request):
    retorno = []
    tag = ''
    metodo = ''
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)
        #quant = Estoque arrigo /// obs = Estoque koala
        skus = [
            [tudo['sku1'],tudo['quant1'],tudo['obs1']],
            [tudo['sku2'],tudo['quant2'],tudo['obs2']],
            [tudo['sku3'],tudo['quant3'],tudo['obs3']],
            [tudo['sku4'],tudo['quant4'],tudo['obs4']],
            [tudo['sku5'],tudo['quant5'],tudo['obs5']],
            [tudo['sku6'],tudo['quant6'],tudo['obs6']],
            [tudo['sku7'],tudo['quant7'],tudo['obs7']],
            [tudo['sku8'],tudo['quant8'],tudo['obs8']],
            [tudo['sku9'],tudo['quant9'],tudo['obs9']],
            [tudo['sku10'],tudo['quant10'],tudo['obs10']],
        ]
        for n in range(0,len(skus)):
            sku = skus[n]
            if len(str(sku[0])) <= 0:
                break
            else:
                print(n,sku[0],sku[1],sku[2])
                if len(str(sku[1])) <= 0:
                    sku[1] = 0
                if len(str(sku[2])) <= 0:
                    sku[2] = 0

            try:
                estoque = Estoque_arrigo.objects.get(EA_sku=str(sku[0]))
                log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_arrigo",LE_novo_valor=int(sku[1]),LE_antigo_valor=estoque.EA_estoque_arrigo,LE_user=str(request.user))
                estoque.EA_estoque_arrigo = int(sku[1])
                log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_koala",LE_novo_valor=int(sku[2]),LE_antigo_valor=estoque.EA_estoque_koala,LE_user=str(request.user))
                estoque.EA_estoque_koala = int(sku[2])
                log = Log_estoques.objects.create(LE_sku=estoque,LE_campo="EA_estoque_total",LE_novo_valor=int(int(sku[1])+int(sku[2])),LE_antigo_valor=estoque.EA_estoque_total,LE_user=str(request.user))
                estoque.EA_estoque_total = int(sku[1]) + int(sku[2])
                estoque.save()
            except:
                try:
                    prod = Produto.objects.get(Pro_Sku=str(sku[0]))
                    titulo = prod.Pro_Nome
                except:
                    titulo = None
                estoque = Estoque_arrigo.objects.create(EA_sku=str(sku[0]),EA_titulo=titulo,EA_estoque_arrigo=int(sku[1]),EA_estoque_koala=int(sku[2]),EA_estoque_total=int(int(sku[1])+int(sku[2])))
        
        retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})
    else:
        return render(request, 'pedidos/novoestoque.html',{"lista_skus":retorno})


@login_required
def conexaoeditar(request):
    retorno = []
    tipo = ''
    if request.method == 'POST':
        tudo = request.POST.copy()
        tudo = json.dumps(tudo)
        tudo = json.loads(tudo)
        print(tudo)

        try:
            tipo = tudo['Baixa']
            tipo = 'baixa'
            tag = 'Baixa'
            metodo = 'BaixaEstoque'
        except:
            try:
                tipo = tudo['Adicionar']
                tipo = 'add'
                tag = 'Adicionar'
                metodo = 'AdicionaEstoque'
            except:
                retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
                return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})

        if tipo == 'baixa':
            retorno = Estoque_arrigo.objects.filter(EA_sku=str(tudo['Baixa']))
        elif tipo == 'add':
            retorno = Estoque_arrigo.objects.filter(EA_sku=str(tudo['Adicionar']))

        return render(request, 'pedidos/editarestoque.html',{"lista_skus":retorno,'tag':tag,'metodo':metodo})
    else:
        retorno = Estoque_arrigo.objects.all().order_by("EA_sku")
        return render(request, 'pedidos/estoque.html',{"lista_skus":retorno})


