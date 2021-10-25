#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
#Import Models
from sincronizador.models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view
from produtos.models import Produto, Preco_Portal, Confere_Preco_log, Nota, Kit
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
        nfs =  Nota.objects.filter(NT_visualizado=False)
        for n in range(0,len(nfs)):
            nota = nfs[n]
            nota.NT_visualizado = True
            nota.save()
    else:
        for n in range(0,len(nfs)):
            nota = nfs[n]
            numero = nota.NT_Num_NF
            forn = nota.NT_fornecedor
            produtos = str(nota.NT_produtos)
            produtos = produtos.replace("[","")
            produtos = produtos.replace("]","")
            produtos = produtos.replace("'","")
            produtos = produtos.replace('"','')
            produtos = produtos.replace(" ","")
            produtos = produtos.split(",")
            for nn in range(0,len(produtos)):
                skuh = produtos[nn]
                if str(skuh[:2]) == "KT":
                    continue
                else:
                    try:
                        prods = Produto.objects.get(Pro_sku=skuh)
                        skuu = prods.Pro_sku
                    except:
                        continue
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

    url = "http://189.103.128.254:2082/root/estoque/"+str(vetor['Codigo'])
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
        create = Produto_Precificacao.objects.create(PP_ID = int(vetor['Codigo']),PP_sku = prodss, PP_nome = str(vetor['Nome']), PP_estoque_fisico = int(estoqueatual), PP_fornecedor = str(fornecedor), PP_custo = float(custo), PP_custo_adm = float(comiss.CS_Custo_Adm), PP_imposto = float(comiss.CS_Impostos), PP_Classificao_total_absoluta = False, PP_Classificao_total = 0, PP_comissao_site_absoluta = False, PP_comissao_site = float(comiss.CS_Comissao_site), PP_Faixa_Portal = faixa_portal, PP_Faixa_Site = faixa_site,PP_Amazon_KES_absoluta = False, PP_Amazon_KES = float(comiss.CS_Amazon_Comissao), PP_B2W_ALK_absoluta = False, PP_B2W_ALK = float(comiss.CS_B2W_ALK_Comissao), PP_B2W_GEA_absoluta = False, PP_B2W_GEA = float(comiss.CS_B2W_GEA_Comissao), PP_B2W_JCMA_absoluta = False, PP_B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao), PP_B2W_KC_absoluta = False, PP_B2W_KC = float(comiss.CS_B2W_KC_Comissao), PP_Carrefour_ALK_absoluta = False, PP_Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao), PP_Carrefour_GEA_absoluta = False, PP_Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao), PP_Centauro_ALK_absoluta = False, PP_Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao), PP_Cnova_KES_absoluta = False, PP_Cnova_KES = float(comiss.CS_Cnova_KES_Comissao), PP_MadeiraMadeira_KES_absoluta = False, PP_MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao), PP_Magalu_GEA_absoluta = False, PP_Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao), PP_Magalu_KC_absoluta = False, PP_Magalu_KC = float(comiss.CS_Magalu_KC_Comissao), PP_Netshoes_KES_absoluta = False, PP_Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao), PP_Netshoes_ALK_absoluta = False, PP_Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao))
        print(vetor['Codigo'], "cadastrdo")
