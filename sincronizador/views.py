#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
#Import Models
from .models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view
from produtos.models import Produto, Preco_Portal, Confere_Preco_log, Produto_Precificacao, Fornecedores, Nota, Kit
from vendas.models import Venda
from precos.models import Preco_Faixa, Comissoes
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

sinc_open  = get_object_or_404(Sinc_open, pk='1')
sinc_open.SO_status = False
sinc_open.save()



firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
db = firebase.database()

def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote

def remove_repetidos(lista):
    l = []
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
    return l

def importar(id_master):
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

    ip = str(Master.SC_ip)
    url = "http://"+str(ip)+":2082/root/estoque/"+str(vetor['Codigo'])
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
        create = Produto_Precificacao.objects.create(PP_ID = int(vetor['Codigo']),PP_sku = prodss, PP_nome = str(vetor['Nome']), PP_estoque_fisico = int(estoqueatual), PP_fornecedor = str(fornecedor), PP_custo = float(custo),PP_custo_adm_site=float(comiss.CS_Custo_Adm_site), PP_custo_adm_portal = float(comiss.CS_Custo_Adm_portal), PP_imposto = float(comiss.CS_Impostos), PP_Classificao_total_absoluta = False, PP_Classificao_total = 0, PP_comissao_site_absoluta = False, PP_comissao_site = float(comiss.CS_Comissao_site), PP_Faixa_Portal = faixa_portal, PP_Faixa_Site = faixa_site,PP_Amazon_KES_absoluta = False, PP_Amazon_KES = float(comiss.CS_Amazon_Comissao), PP_B2W_ALK_absoluta = False, PP_B2W_ALK = float(comiss.CS_B2W_ALK_Comissao), PP_B2W_GEA_absoluta = False, PP_B2W_GEA = float(comiss.CS_B2W_GEA_Comissao), PP_B2W_JCMA_absoluta = False, PP_B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao), PP_B2W_KC_absoluta = False, PP_B2W_KC = float(comiss.CS_B2W_KC_Comissao), PP_Carrefour_ALK_absoluta = False, PP_Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao), PP_Carrefour_GEA_absoluta = False, PP_Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao), PP_Centauro_ALK_absoluta = False, PP_Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao), PP_Cnova_KES_absoluta = False, PP_Cnova_KES = float(comiss.CS_Cnova_KES_Comissao), PP_MadeiraMadeira_KES_absoluta = False, PP_MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao), PP_Magalu_GEA_absoluta = False, PP_Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao), PP_Magalu_KC_absoluta = False, PP_Magalu_KC = float(comiss.CS_Magalu_KC_Comissao), PP_Netshoes_KES_absoluta = False, PP_Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao), PP_Netshoes_ALK_absoluta = False, PP_Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao))
        print(vetor['Codigo'], "cadastrdo")


# Isso faz com que a tarefa fique rodando em backgrounf de forma asincrona // ou era o que eu achava
@background(schedule=0)
def start_sinc():
#--------------- Verifica se o sinc está aberto ---------------

    sinc_open  = get_object_or_404(Sinc_open, pk='1')
    if sinc_open.SO_status == True:
        return 0
    else:
        sinc_open  = get_object_or_404(Sinc_open, pk='1')
        sinc_open.SO_status = True
        sinc_open.save()
#--------------- Loop Produtos ---------------
    for _ in iter(int, 1):
#--------------- Config API Master ---------------

        Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
        headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
        ip = str(Master.SC_ip) #Ip ou link da api
        print(ip)
#--------------- Obter Produtos ---------------

        url = "http://"+ip+":2082/root/produto/"
        try:
            
            response = requests.request("GET", url, headers=headers)
        except:
            print("Sinc fechado erro ao obter informações da api!")
            sinc_open  = get_object_or_404(Sinc_open, pk='1')
            sinc_open.SO_status = False
            sinc_open.save()
            return 0
        response = response.text.encode('utf8')
        data = json.loads(response)
        produtos = data['produto']
        if len(produtos) >= 1:
            for n in range(0,len(produtos)):

                Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
                headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
                ip = str(Master.SC_ip) #Ip ou link da api
#---------------- Ignorar produto 'Inativo' -------------------------
                estoqueloja = 0   
                estoquebarracao = 0
                vetor = produtos[n]
                sku = vetor['Referencia']
                if sku == 'INATIVO':
                    url = "http://"+ip+":2082/root/produto/" + str(vetor['Codigo']) + "/ok"
                    try:
                        response = requests.request("POST", url, headers=headers)
                    except:
                        print("Sinc fechado erro ao obter informações da api!")
                        sinc_open  = get_object_or_404(Sinc_open, pk='1')
                        sinc_open.SO_status = False
                        sinc_open.save()
                        return 0
                    continue
#---------------- Estoque produto -------------------------
                
                url = "http://"+str(ip)+":2082/root/estoque/"+str(vetor['Codigo'])
                try:
                    response = requests.request("GET", url, headers=headers)
                except:
                    print("Sinc fechado erro ao obter informações da api!")
                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                    sinc_open.SO_status = False
                    sinc_open.save()
                    return 0
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
                try:
                    response = requests.request("POST", url, headers=headers)
                except:
                    print("Sinc fechado erro ao obter informações da api!")
                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                    sinc_open.SO_status = False
                    sinc_open.save()
                    return 0

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
#---------------- Nome do log -------------------------

                data_e_hora_atuais = datetime.now()
                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')

                name = 'Master Produto | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
#---------------- Analisa mudança de preço para loja -------------------------


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
#---------------- Integra ou atualiza produto no Banco -------------------------
                if str(nome)[:2] == "KT":
                    for comp in range(0,len(vetor['Composicao'])):
                        composi = vetor['Composicao'][comp]
                        composi = composi['ProdutoCodigo']
                        try:
                            prodsss = Produto.objects.get(pk=str(composi))
                            sku_princ = str(prodsss.Pro_Sku)
                        except Produto.DoesNotExist:
                            try:
                                importar(composi)
                                prodsss = Produto.objects.get(pk=str(composi))
                                sku_princ = str(prodsss.Pro_Sku)
                            except:
                                print(n,composi,"Produto não importado")
                                continue
                        try:
                            kit = Kit.objects.get(KT_principal = composi)
                            kt = str(kit.KT_variacoes)
                            kt = kt.replace("[","")
                            kt = kt.replace("]","")
                            kt = kt.replace("'","")
                            kt = kt.replace('"','')
                            kt = kt.replace(" ","")
                            kt = kt.split(",")
                            kt_antigo = kt
                            kt.append(str(vetor['Referencia']))
                            kt = remove_repetidos(kt)
                            if str(kt) == str(kt_antigo):
                                print(composi,"Ja cadastrado")
                                continue
                            else:
                                kit.KT_variacoes = kt
                                kit.save()
                                print(composi,"Atualizado")
                        except:
                            kt = str(vetor['Referencia'])
                            kt = kt.split()
                            kit = Kit.objects.create(KT_principal=prodsss,KT_variacoes=kt,KT_principal_Sku=str(prodsss.Pro_Sku))
                            print(composi,"cadastrado")
                            


                            

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
                    #print(n,vetor['Referencia'],'Update no banco!')	
                    prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                    sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoVenda'], SL_PrecoPor = vetor['PrecoFicticioSite'], SL_Estoque = estoqueatual)


                except Produto.DoesNotExist:
                    Produto(Pro_Id = vetor['Codigo'], Pro_Sku = str(nome), Pro_Nome = vetor['Nome'], Pro_EstoqueBarracao = estoquebarracao, Pro_Loja = estoqueloja, Pro_EstoqueTotal = estoqueatual, Pro_Ean = vetor['EAN'], Pro_Ativo = vetor['Ativo'], Pro_LocalizacaoSetor = vetor['LocalizacaoSetor'], Pro_LocalizacaoBox = vetor['LocalizacaoBox'], Pro_SemEan = vetor['SubstituirEANPorSemGTIN'], Pro_FornecedorCodigo = vetor['FornecedorCodigo'], Pro_FabricanteCodigo = vetor['FabricanteCodigo'], Pro_Classificacao = vetor['Classificacao'], Pro_Modelo = vetor['Modelo'], Pro_Conteudo = vetor['Conteudo'], Pro_DescricaoCurta = vetor['DescricaoCurta'], Pro_DescricaoLonga = vetor['DescricaoLonga'], Pro_PrecoCusto = vetor['PrecoCusto'], Pro_PrecoVenda = vetor['PrecoVenda'], Pro_PrecoFicticio = str(vetor['PrecoFicticioSite']), Pro_Altura = vetor['Altura'], Pro_Largura = vetor['Largura'], Pro_Profundidade = vetor['Profundidade'], Pro_Peso = vetor['Peso'], Pro_NCM = vetor['NCM'], Pro_Composicao = vetor['Composicao'], Pro_CategoriaPrincipal = vetor['CategoriaPrincipal'], Pro_DisponibilidadeEmEstoque = vetor['DisponibilidadeEmEstoque'], Pro_DisponibilidadeSemEstoque = vetor['DisponibilidadeSemEstoque'], Pro_PromocaoInicio = vetor['PromocaoInicio'], Pro_PromocaoFim = vetor['PromocaoFim'], Pro_PrevalecerPrecoPai = vetor['PrevalecerPrecoPai'], Pro_Taxa = vetor['Taxa'], Pro_NumeroMaximoParcelas = vetor['NumeroMaximoParcelas'], Pro_EstoqueMaximo = EstoqueMaximo, Pro_TipoDisponibilidade = vetor['TipoDisponibilidade'], Pro_PreVenda = vetor['PreVenda'], Pro_PreVendaData = vetor['PreVendaData'], Pro_PreVendaLimite = vetor['PreVendaLimite'], Pro_VendaSemEstoque = vetor['VendaSemEstoque'], Pro_VendaSemEstoqueData = vetor['VendaSemEstoqueData'], Pro_VendaSemEstoqueLimite = vetor['VendaSemEstoqueLimite'], Pro_ExibirDisponibilidade = vetor['ExibirDisponibilidade'], Pro_TipoReposicao = vetor['TipoReposicao'], Pro_PesoCubico = vetor['PesoCubico'], Pro_QuantidadeMaximaPorCliente = vetor['QuantidadeMaximaPorCliente'], Pro_FreteGratis = vetor['FreteGratis'], Pro_TituloVariacao = vetor['TituloVariacao'], Pro_TituloSubVariacao = vetor['TituloSubVariacao'], Pro_MetaTitle = vetor['MetaTitle'], Pro_MetaDescription = vetor['MetaDescription'], Pro_MetaKeywords = vetor['MetaKeywords'], Pro_PalavrasParaPesquisa = vetor['PalavrasParaPesquisa'], Pro_Ordem = vetor['Ordem'], Pro_VisualizarUrlDireto = vetor['VisualizarUrlDireto'], Pro_TemOpcaoPresente = vetor['TemOpcaoPresente'], Pro_PresenteValor = float(vetor['PresenteValor']), Pro_Video = vetor['Video'], Pro_UnidadeSigla = vetor['UnidadeSigla'], Pro_Foto = vetor['Foto'], Pro_ControlaEstoque = vetor['ControlaEstoque'], Pro_Fornecedores = vetor['Fornecedores'], Pro_Imagens = vetor['Imagens'], Pro_CodigoPai = vetor['CodigoPai'], Pro_EstoqueSite = vetor['EstoqueSite'], Pro_Composto = vetor['Composto'], Pro_Grade = vetor['Grade'], Pro_QuantidadeTerceiros = QuantidadeTerceiros, Pro_CST = vetor['CST'], Pro_NomeAbreviado = vetor['NomeAbreviado'], Pro_IPICST = vetor['IPICST'], Pro_PISCST = vetor['PISCST'], Pro_COFINSCST = vetor['COFINSCST'], Pro_PISAliquota = float(vetor['PISAliquota']), Pro_COFINSAliquota = float(vetor['COFINSAliquota']), Pro_CFOPCodigo = vetor['CFOPCodigo'], Pro_ICMSTipo = vetor['ICMSTipo'], Pro_ICMSST = float(vetor['ICMSST']), Pro_CSTOrigem = vetor['CSTOrigem'], Pro_PrecoFicticioSite = vetor['PrecoFicticioSite'], Pro_PrecoSite = vetor['PrecoSite'], Pro_ICMSVenda = float(vetor['ICMSVenda']), Pro_Volume = vetor['Volume'], Pro_ItensInclusos = vetor['ItensInclusos'], Pro_DadosTecnicos = vetor['DadosTecnicos'], Pro_Categorias = vetor['Categorias'], Pro_Unidade = vetor['Unidade'], Pro_Thumbnail = vetor['Thumbnail'], Pro_EnviarSite = vetor['EnviarSite'], Pro_Comissao = vetor['Comissao'], Pro_ExibeEsgotado = vetor['ExibeEsgotado'], Pro_CSOSN = vetor['CSOSN'], Pro_CEST = vetor['CEST'], Pro_ICMSCompraAliquota = vetor['ICMSCompraAliquota'], Pro_ICMSSTBase = vetor['ICMSSTBase'], Pro_ICMSReducaoBaseCalculo = vetor['ICMSReducaoBaseCalculo'], Pro_ICMSBase = vetor['ICMSBase'], Pro_IPIAliquota = vetor['IPIAliquota'], Pro_IPICompraAliquota = vetor['IPICompraAliquota'], Pro_ISSAliquota = vetor['ISSAliquota'], Pro_ISSCSERV = vetor['ISSCSERV'], Pro_Lista = vetor['Lista'], Pro_GrupoTributacao = vetor['GrupoTributacao'], Pro_DefinicaoPrecoEscopo = vetor['DefinicaoPrecoEscopo'], Pro_VtexLojasId = vetor['VtexLojasId'], Pro_DefinicaoProdutoCodigo = vetor['DefinicaoProdutoCodigo'], Pro_Slug = vetor['Slug'], Pro_AtrelamentoDescricao = vetor['AtrelamentoDescricao'], Pro_BeneficiosDescricao = vetor['BeneficiosDescricao'], Pro_DestaqueDescricao = vetor['DestaqueDescricao'], Pro_PromocaoDescricao = vetor['PromocaoDescricao'], Pro_GanheBrindeDescricao = vetor['GanheBrindeDescricao'], Pro_LancamentoDescricao = vetor['LancamentoDescricao'], Pro_MedidasDescricao = vetor['MedidasDescricao'], Pro_QuemUsaDescricao = vetor['QuemUsaDescricao'], Pro_SeguroDescricao = vetor['SeguroDescricao'], Pro_SugestaoDeUsoDescricao = vetor['SugestaoDeUsoDescricao'], Pro_PercentualMarkupPrecoMargem = vetor['PercentualMarkupPrecoMargem'], Pro_PrecoPercentual = vetor['PrecoPercentual'], Pro_PrevalecerPromoPai = vetor['PrevalecerPromoPai'], Pro_PontosFidelidade = vetor['PontosFidelidade'], Pro_SemEntregas = vetor['SemEntregas'], Pro_ExibirNovo = vetor['ExibirNovo'], Pro_ExibirNovoInicio = vetor['ExibirNovoInicio'], Pro_ExibirNovoFim = vetor['ExibirNovoFim'], Pro_EstoqueMinimoIndisponibilizar = vetor['EstoqueMinimoIndisponibilizar'], Pro_EstoqueMinimoNotificar = vetor['EstoqueMinimoNotificar'], Pro_ExibirProdutoInicio = vetor['ExibirProdutoInicio'], Pro_ExibirProdutoFim = vetor['ExibirProdutoFim'], Pro_CoreExibirPreco = vetor['CoreExibirPreco'], Pro_BundleOpcao = vetor['BundleOpcao'], Pro_Flag = vetor['Flag'], Pro_Acabamento = vetor['Acabamento'], Pro_AnoPublicacao = vetor['AnoPublicacao'], Pro_Assunto = vetor['Assunto'], Pro_Autor = vetor['Autor'], Pro_Colecao = vetor['Colecao'], Pro_Edicao = vetor['Edicao'], Pro_Editora = vetor['Editora'], Pro_Formato = vetor['Formato'], Pro_Idioma = vetor['Idioma'], Pro_ISBN = vetor['ISBN'], Pro_ISBN13 = vetor['ISBN13'], Pro_Pagina = vetor['Pagina'], Pro_Titulo = vetor['Titulo'], Pro_Tradutor = vetor['Tradutor'], Pro_CamposRelacionaveis = vetor['CamposRelacionaveis'], Pro_Editor = vetor['Editor'], Pro_Ilustrador = vetor['Ilustrador'], Pro_Organizador = vetor['Organizador'], Pro_Fotografo = vetor['Fotografo'], Pro_PaisOrigem = vetor['PaisOrigem'], Pro_DataPublicacao = vetor['DataPublicacao'], Pro_NVolume = vetor['NVolume'], Pro_EditaSinopse = vetor['EditaSinopse'], Pro_BarraExtra = vetor['BarraExtra']).save()
                    prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                    sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = vetor['PrecoFicticioSite'], SL_PrecoPor = vetor['PrecoVenda'], SL_Estoque = estoqueatual)
                    #print(n,vetor['Referencia'],'Cadastrado no banco!')
#---------------- Ok para a fila de integração do master -------------------------


                try:
                    try:
                        url = "http://"+ip+":2082/root/produto/" + str(vetor['Codigo']) + "/ok"
                    except:
                        print("Sinc fechado erro ao obter informações da api!")
                        sinc_open  = get_object_or_404(Sinc_open, pk='1')
                        sinc_open.SO_status = False
                        sinc_open.save()
                        return 0
                    response = requests.request("POST", url, headers=headers)
                    

                except:

                    print("Sinc fechado erro ao obter informações da api!")
                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                    sinc_open.SO_status = False
                    sinc_open.save()
                    return 0
#---------------- Integra moveis no Firebase -------------------------
                if vetor['FabricanteCodigo'] == 916 or vetor['FabricanteCodigo'] == '916':
                    data = {}
                    data['SKU'] = vetor['Referencia']
                    data['ID_master'] = vetor['Codigo']
                    data['Titulo'] = vetor['Nome']
                    data['Preco_tabela'] = vetor['PrecoVenda']		

                    db.child("Produtos").child(vetor['Referencia']).set(data)
                    print(vetor['Referencia'],'arrigo')
# ---------------- Salvar produto_precificacao -------------------------

                custo = vetor['PrecoCusto']
                custo = custo.replace('"','')
                custo = custo.replace("'","")
                custo = float(custo)

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
                    classificacao = PRO_LUC.PP_Faixa_Site

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
                    classificacao = PRO_LUC.PP_Faixa_Site

                faixa_site = classificacao

                try:
                    comiss = get_object_or_404(Comissoes, pk='1')
                    PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))

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
                                precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                                if custo <= 4.99:
                                    classificacao = a0_a_4_99
                                    site = float(precofaixa.PF_0_a_4_99)
                                elif custo >= 5 and custo <= 14.99:
                                    classificacao = a5_a_14_99
                                    site = float(precofaixa.PF_5_a_14_99)
                                elif custo >= 15 and custo <= 29.99:
                                    classificacao = a15_a_29_99
                                    site = float(precofaixa.PF_15_a_29_99) 
                                elif custo >= 30 and custo <= 49.99:
                                    classificacao = a30_a_49_99
                                    site = float(precofaixa.PF_30_a_49_99)
                                elif custo >= 50 and custo <= 79.99:
                                    classificacao = a50_a_79_99
                                    site = float(precofaixa.PF_50_a_79_99)
                                elif custo >= 80 and custo <= 119.99:
                                    classificacao = a80_a_119_99
                                    site = float(precofaixa.PF_80_a_119_99)
                                elif custo >= 120 and custo <= 149.99:
                                    classificacao = a120_a_149_99
                                    site = float(precofaixa.PF_120_a_149_99)
                                elif custo >= 150 and custo <= 199.99:
                                    classificacao = a150_a_199_99
                                    site = float(precofaixa.PF_150_a_199_99)
                                elif custo >= 200 and custo <= 249.99:
                                    classificacao = a200_a_249_99
                                    site = float(precofaixa.PF_200_a_249_99)
                                elif custo >= 250 and custo <= 299.99:
                                    classificacao = a250_a_299_99
                                    site = float(precofaixa.PF_250_a_299_99)
                                elif custo >= 300 and custo <= 349.99:
                                    classificacao = a300_a_349_99
                                    site = float(precofaixa.PF_300_a_349_99)
                                elif custo >= 350 and custo <= 399.99:
                                    classificacao = a350_a_399_99
                                    site = float(precofaixa.PF_350_a_399_99)
                                elif custo >= 400 and custo <= 449.99:
                                    classificacao = a400_a_449_99
                                    site = float(precofaixa.PF_400_a_449_99)
                                elif custo >= 450 and custo <= 549.99:
                                    classificacao = a450_a_549_99
                                    site = float(precofaixa.PF_450_a_549_99)
                                elif custo >= 550 and custo <= 649.99:
                                    classificacao = a550_a_649_99
                                    site = float(precofaixa.PF_550_a_649_99)
                                elif custo >= 650 and custo <= 749.99:
                                    classificacao = a650_a_749_99
                                    site = float(precofaixa.PF_650_a_749_99)
                                elif custo >= 750 and custo <= 899.99:
                                    classificacao = a750_a_899_99
                                    site = float(precofaixa.PF_750_a_899_99)
                                elif custo >= 900 and custo <= 999.99:
                                    classificacao = a900_a_999_99
                                    site = float(precofaixa.PF_900_a_999_99)
                                elif custo >= 1000 and custo <= 1499.99:
                                    classificacao = a1000_a_1499_99
                                    site = float(precofaixa.PF_1000_a_1499_99)
                                elif custo >= 1500 and custo <= 1999.99:
                                    classificacao = a1500_a_1999_99
                                    site = float(precofaixa.PF_1500_a_1999_99)
                                elif custo >= 2000 and custo <= 2499.99:
                                    classificacao = a2000_a_2499_99
                                    site = float(precofaixa.PF_2000_a_2499_99)
                                elif custo >= 2500 and custo <= 2999.99:
                                    classificacao = a2500_a_2999_99
                                    site = float(precofaixa.PF_2500_a_2999_99)
                                elif custo >= 3000:
                                    classificacao = maior_3000
                                    site = float(precofaixa.PF_maior_3000)
                            else:
                                classificacao = PRO_LUC.PP_Faixa_Site

                            if PRO_LUC.PP_comissao_site_absoluta != True:
                                PRO_LUC.PP_comissao_site = comiss.CS_Comissao_site
                            
                            if PRO_LUC.PP_Amazon_KES_absoluta != True:
                                PRO_LUC.PP_Amazon_KES = classificacao
                            
                            if PRO_LUC.PP_B2W_ALK_absoluta != True:
                                PRO_LUC.PP_B2W_ALK = classificacao

                            if PRO_LUC.PP_B2W_GEA_absoluta != True:
                                PRO_LUC.PP_B2W_GEA = classificacao                              

                            if PRO_LUC.PP_B2W_JCMA_absoluta != True:
                                PRO_LUC.PP_B2W_JCMA = classificacao

                            if PRO_LUC.PP_B2W_KC_absoluta != True:
                                PRO_LUC.PP_B2W_KC = classificacao

                            if PRO_LUC.PP_Carrefour_ALK_absoluta != True:
                                PRO_LUC.PP_Carrefour_ALK = classificacao

                            if PRO_LUC.PP_Carrefour_GEA_absoluta != True:
                                PRO_LUC.PP_Carrefour_GEA = classificacao

                            if PRO_LUC.PP_Centauro_ALK_absoluta != True:
                                PRO_LUC.PP_Centauro_ALK = classificacao

                            if PRO_LUC.PP_Cnova_KES_absoluta != True:
                                PRO_LUC.PP_Cnova_KES = classificacao

                            if PRO_LUC.PP_MadeiraMadeira_KES_absoluta != True:
                                PRO_LUC.PP_MadeiraMadeira_KES = classificacao

                            if PRO_LUC.PP_Magalu_GEA_absoluta != True:
                                PRO_LUC.PP_Magalu_GEA = classificacao

                            if PRO_LUC.PP_Magalu_KC_absoluta != True:
                                PRO_LUC.PP_Magalu_KC = classificacao
                            
                            if PRO_LUC.PP_Netshoes_KES_absoluta != True:
                                PRO_LUC.PP_Netshoes_KES = classificacao
                            
                            if PRO_LUC.PP_Netshoes_ALK_absoluta != True:
                                PRO_LUC.PP_Netshoes_ALK = classificacao

                            PRO_LUC.PP_Faixa_Portal = classificacao
                        
                        if PRO_LUC.PP_Faixa_Site_absoluta != True:
                            PRO_LUC.PP_Faixa_Site = site
                            PRO_LUC.PP_tipo_produto = Master_LocalizacaoSetor

                        PRO_LUC.PP_tipo_produto = Master_LocalizacaoSetor
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

                    create = Produto_Precificacao.objects.create(PP_ID = int(vetor['Codigo']),PP_sku = prodss, PP_nome = str(vetor['Nome']), PP_estoque_fisico = int(estoqueatual), PP_fornecedor = str(fornecedor), PP_custo = float(custo),PP_custo_adm_site=float(comiss.CS_Custo_Adm_site), PP_custo_adm_portal = float(comiss.CS_Custo_Adm_portal), PP_imposto = float(comiss.CS_Impostos), PP_Classificao_total_absoluta = False, PP_Classificao_total = 0, PP_comissao_site_absoluta = False, PP_comissao_site = float(comiss.CS_Comissao_site), PP_Faixa_Portal = faixa_portal, PP_Faixa_Site = faixa_site,PP_Amazon_KES_absoluta = False, PP_Amazon_KES = float(comiss.CS_Amazon_Comissao), PP_B2W_ALK_absoluta = False, PP_B2W_ALK = float(comiss.CS_B2W_ALK_Comissao), PP_B2W_GEA_absoluta = False, PP_B2W_GEA = float(comiss.CS_B2W_GEA_Comissao), PP_B2W_JCMA_absoluta = False, PP_B2W_JCMA = float(comiss.CS_B2W_JCMA_Comissao), PP_B2W_KC_absoluta = False, PP_B2W_KC = float(comiss.CS_B2W_KC_Comissao), PP_Carrefour_ALK_absoluta = False, PP_Carrefour_ALK = float(comiss.CS_Carrefour_ALK_Comissao), PP_Carrefour_GEA_absoluta = False, PP_Carrefour_GEA = float(comiss.CS_Carrefour_GEA_Comissao), PP_Centauro_ALK_absoluta = False, PP_Centauro_ALK = float(comiss.CS_Centauro_ALK_Comissao), PP_Cnova_KES_absoluta = False, PP_Cnova_KES = float(comiss.CS_Cnova_KES_Comissao), PP_MadeiraMadeira_KES_absoluta = False, PP_MadeiraMadeira_KES = float(comiss.CS_MM_KES_Comissao), PP_Magalu_GEA_absoluta = False, PP_Magalu_GEA = float(comiss.CS_Magalu_GEA_Comissao), PP_Magalu_KC_absoluta = False, PP_Magalu_KC = float(comiss.CS_Magalu_KC_Comissao), PP_Netshoes_KES_absoluta = False, PP_Netshoes_KES = float(comiss.CS_Netshoes_KES_Comissao), PP_Netshoes_ALK_absoluta = False, PP_Netshoes_ALK = float(comiss.CS_Netshoes_ALK_Comissao))
                    print(vetor['Codigo'], "cadastrdo")
                    #print(vetor['Codigo'], 'criado Produto_Precificacao')
# --------------- Variaveis de calculo de preço Portais --------------- #
                try:
                    PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))

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


                    

                    portais = [
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

                    imposto = float(PRO_LUC.PP_imposto)/100
                    

                    CustoAdmin = float(PRO_LUC.PP_custo_adm_portal)/100
                    

                    comissao = float(PRO_LUC.PP_comissao_site)/100
                    comissao = float(comissao/100)


                except:
                    print("Portais, Erro ao obter faixas de portais, utilizando faixa modelo! ")
                    portais = [
                        {'nome':'Amazon-KES','comissao':0.12,'ID_catalogo':2624,'classificacao':classificacao,},
                        {'nome':'B2W-ALK','comissao':0.158,'ID_catalogo':2780,'classificacao':classificacao,},
                        {'nome':'B2W-GEA','comissao':0.16,'ID_catalogo':2787,'classificacao':classificacao,},
                        {'nome':'B2W-JCMA','comissao':0.16,'ID_catalogo':2994,'classificacao':classificacao,},
                        {'nome':'B2W-KC','comissao':0.163,'ID_catalogo':2786,'classificacao':classificacao,},
                        {'nome':'Carrefour-ALK','comissao':0.12,'ID_catalogo':2640,'classificacao':classificacao,},
                        {'nome':'Carrefour-GEA','comissao':0.12,'ID_catalogo':2918,'classificacao':classificacao,},
                        {'nome':'Centauro-ALK','comissao':0.20,'ID_catalogo':3003,'classificacao':classificacao,},
                        {'nome':'Cnova-KES','comissao':0.1250,'ID_catalogo':2648,'classificacao':classificacao,},
                        {'nome':'MadeiraMadeira-KES','comissao':0.11,'ID_catalogo':2342,'classificacao':classificacao,},
                        {'nome':'Magalu-GEA','comissao':0.13,'ID_catalogo':2829,'classificacao':classificacao,},
                        {'nome':'Magalu-KC','comissao':0.128,'ID_catalogo':2587,'classificacao':classificacao,},
                        {'nome':'Netshoes-KES','comissao':0.20,'ID_catalogo':2584,'classificacao':classificacao,},
                        {'nome':'Netshoes-ALK','comissao':0.20,'ID_catalogo':2440,'classificacao':classificacao,}
                    ]
                    imposto = 0.117 #fixo
                    CustoAdmin = 0.13 #fixo
# --------------- "logar" na omni --------------- #
                headers = {
                    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.267',
                }

                login_data = {
                    'Email': 'exemplo@email.com',
                    'Password': 'senha123',
                    'RememberMe': 'false',
                }

                cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

                sku = str(vetor['Referencia'])
                # --------------- Script altereação --------------- #
                with requests.Session() as r:
                    #sku = str(input('Digite o SKU: '))

                    url = 'https://admin.fomnichannel.com.br/Account/Login?ReturnUrl=%2FGerenciador%2FDashboard'
                    try:
                        response = r.get(url, headers=headers)
                    except:
                        continue
                    soup = BeautifulSoup(response.content, 'html5lib')
                    tree = html.fromstring(response.content)
                    buyers = tree.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
                    __RequestVerificationToken = '__RequestVerificationToken='+str(buyers)
                    headers = {
                        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.267',
                        'Referer':'https://admin.fomnichannel.com.br/Gerenciador/Produto'
                    }
                    login_data['__RequestVerificationToken'] = str(buyers)
                    try:
                        response = r.post(url, data=login_data, headers=headers)
                    except:
                        continue
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
                    try:
                        response = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/LoadGrid',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(prod_data))
                    #try:
                        json_prod = response.json()
                    except:
                        continue
                    id_prod = json_prod['aaData']
                    for num in range(0,len(id_prod)):
                        textprod = id_prod[num]
                        get_produto = {
                                'produtoId':str(textprod[0]),
                            }
                        try:
                            get_ = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/GetStatusProduto/',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(get_produto))
                            
                            response = r.post('https://admin.fomnichannel.com.br/Gerenciador/Produto/GetStatusProduto/',headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(get_produto))
                            
                            url = 'https://admin.fomnichannel.com.br/Gerenciador/Produto/LoadGridMapeamentoVariantes?produtoId=' + str(textprod[0])
                            
                            response = r.post(url,headers={"Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(mapeamentovariante_data))

                            json_prod = response.json()
                        except:
                            continue
                        if len(json_prod['aaData']) == 0:
                            continue                     
                        
                        else:
                            try:
                                sku_prod = json_prod['aaData']
                                sku_prod = sku_prod[0]
                                sku_prod = sku_prod[0]
                                
                            except:
                                data_e_hora_atuais = datetime.now()
                                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                                name = 'Não encontrado Omni | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)

                                continue
                    try:
                        if len(sku_prod) == 0:
                            print(sku, 'não encontrado na omni')
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'Não encontrado Omni | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                            
                            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)

                            continue
                    except:
                        data_e_hora_atuais = datetime.now()
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        name = 'Não encontrado Omni | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                        
                        prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                        sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Omni", SL_PrecoDe = custo, SL_PrecoPor = 0, SL_Estoque = 0)

                        continue

                    if str(sku_prod) == sku:
# --------------- Obter informações de faixas e custos --------------- #

                        custo = vetor['PrecoCusto']
                        custo = custo.replace('"','')
                        custo = custo.replace("'","")
                        custo = float(custo)


                        Master_LocalizacaoSetor = vetor['LocalizacaoSetor']
                        Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace('"','')
                        Master_LocalizacaoSetor = Master_LocalizacaoSetor.replace("'","")

                        if Master_LocalizacaoSetor == "A":
                            try:
                                precofaixa = Preco_Faixa.objects.get(PF_ID = '5')
                                a0_a_4_99 = float(precofaixa.PF_0_a_4_99)
                                a0_a_4_99 = float(a0_a_4_99/100)

                                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)
                                a5_a_14_99 = float(a5_a_14_99/100)

                                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                                a15_a_29_99 = float(a15_a_29_99/100)
                                
                                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)
                                a30_a_49_99 = float(a30_a_49_99/100)

                                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)
                                a50_a_79_99 = float(a50_a_79_99/100)

                                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)
                                a80_a_119_99 = float(a80_a_119_99/100)

                                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)
                                a120_a_149_99 = float(a120_a_149_99/100)

                                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)
                                a150_a_199_99 = float(a150_a_199_99/100)

                                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)
                                a200_a_249_99 = float(a200_a_249_99/100)

                                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)
                                a250_a_299_99 = float(a250_a_299_99/100)

                                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)
                                a300_a_349_99 = float(a300_a_349_99/100)

                                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)
                                a350_a_399_99 = float(a350_a_399_99/100)

                                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)
                                a400_a_449_99 = float(a400_a_449_99/100)

                                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)
                                a450_a_549_99 = float(a450_a_549_99/100)

                                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)
                                a550_a_649_99 = float(a550_a_649_99/100)

                                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)
                                a650_a_749_99 = float(a650_a_749_99/100)

                                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)
                                a750_a_899_99 = float(a750_a_899_99/100)

                                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)
                                a900_a_999_99 = float(a900_a_999_99/100)

                                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)
                                a1000_a_1499_99 = float(a1000_a_1499_99/100)

                                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)
                                a1500_a_1999_99 = float(a1500_a_1999_99/100)

                                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)
                                a2000_a_2499_99 = float(a2000_a_2499_99/100)

                                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)
                                a2500_a_2999_99 = float(a2500_a_2999_99/100)

                                maior_3000 = float(precofaixa.PF_maior_3000)
                                maior_3000 = float(maior_3000/100)
                            except:
                                a0_a_4_99 = 0.30
                                a5_a_14_99 = 0.28
                                a15_a_29_99 = 0.15                             
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
                                a0_a_4_99 = float(a0_a_4_99/100)

                                a5_a_14_99 = float(precofaixa.PF_5_a_14_99)
                                a5_a_14_99 = float(a5_a_14_99/100)

                                a15_a_29_99 = float(precofaixa.PF_15_a_29_99)
                                a15_a_29_99 = float(a15_a_29_99/100)
                                
                                a30_a_49_99 = float(precofaixa.PF_30_a_49_99)
                                a30_a_49_99 = float(a30_a_49_99/100)

                                a50_a_79_99 = float(precofaixa.PF_50_a_79_99)
                                a50_a_79_99 = float(a50_a_79_99/100)

                                a80_a_119_99 = float(precofaixa.PF_80_a_119_99)
                                a80_a_119_99 = float(a80_a_119_99/100)

                                a120_a_149_99 = float(precofaixa.PF_120_a_149_99)
                                a120_a_149_99 = float(a120_a_149_99/100)

                                a150_a_199_99 = float(precofaixa.PF_150_a_199_99)
                                a150_a_199_99 = float(a150_a_199_99/100)

                                a200_a_249_99 = float(precofaixa.PF_200_a_249_99)
                                a200_a_249_99 = float(a200_a_249_99/100)

                                a250_a_299_99 = float(precofaixa.PF_250_a_299_99)
                                a250_a_299_99 = float(a250_a_299_99/100)

                                a300_a_349_99 = float(precofaixa.PF_300_a_349_99)
                                a300_a_349_99 = float(a300_a_349_99/100)

                                a350_a_399_99 = float(precofaixa.PF_350_a_399_99)
                                a350_a_399_99 = float(a350_a_399_99/100)

                                a400_a_449_99 = float(precofaixa.PF_400_a_449_99)
                                a400_a_449_99 = float(a400_a_449_99/100)

                                a450_a_549_99 = float(precofaixa.PF_450_a_549_99)
                                a450_a_549_99 = float(a450_a_549_99/100)

                                a550_a_649_99 = float(precofaixa.PF_550_a_649_99)
                                a550_a_649_99 = float(a550_a_649_99/100)

                                a650_a_749_99 = float(precofaixa.PF_650_a_749_99)
                                a650_a_749_99 = float(a650_a_749_99/100)

                                a750_a_899_99 = float(precofaixa.PF_750_a_899_99)
                                a750_a_899_99 = float(a750_a_899_99/100)

                                a900_a_999_99 = float(precofaixa.PF_900_a_999_99)
                                a900_a_999_99 = float(a900_a_999_99/100)

                                a1000_a_1499_99 = float(precofaixa.PF_1000_a_1499_99)
                                a1000_a_1499_99 = float(a1000_a_1499_99/100)

                                a1500_a_1999_99 = float(precofaixa.PF_1500_a_1999_99)
                                a1500_a_1999_99 = float(a1500_a_1999_99/100)

                                a2000_a_2499_99 = float(precofaixa.PF_2000_a_2499_99)
                                a2000_a_2499_99 = float(a2000_a_2499_99/100)

                                a2500_a_2999_99 = float(precofaixa.PF_2500_a_2999_99)
                                a2500_a_2999_99 = float(a2500_a_2999_99/100)

                                maior_3000 = float(precofaixa.PF_maior_3000)
                                maior_3000 = float(maior_3000/100)
                            except:
                                a0_a_4_99 = 0.40
                                a5_a_14_99 = 0.35
                                a15_a_29_99 = 0.25                             
                                a30_a_49_99 = 0.20
                                a50_a_79_99 = 0.15
                                a80_a_119_99 = 0.13
                                a120_a_149_99 = 0.11
                                a150_a_199_99 = 0.10
                                a200_a_249_99 = 0.09
                                a250_a_299_99 = 0.08
                                a300_a_349_99 = 0.075
                                a350_a_399_99 = 0.07
                                a400_a_449_99 = 0.065
                                a450_a_549_99 = 0.6
                                a550_a_649_99 = 0.055
                                a650_a_749_99 = 0.05
                                a750_a_899_99 = 0.045
                                a900_a_999_99 = 0.04
                                a1000_a_1499_99 = 0.035
                                a1500_a_1999_99 = 0.03
                                a2000_a_2499_99 = 0.03
                                a2500_a_2999_99 = 0.03
                                maior_3000 = 0.03
                        else:
                            a0_a_4_99 = 0.40
                            a5_a_14_99 = 0.35
                            a15_a_29_99 = 0.25                             
                            a30_a_49_99 = 0.20
                            a50_a_79_99 = 0.15
                            a80_a_119_99 = 0.13
                            a120_a_149_99 = 0.11
                            a150_a_199_99 = 0.10
                            a200_a_249_99 = 0.09
                            a250_a_299_99 = 0.08
                            a300_a_349_99 = 0.075
                            a350_a_399_99 = 0.07
                            a400_a_449_99 = 0.065
                            a450_a_549_99 = 0.6
                            a550_a_649_99 = 0.055
                            a650_a_749_99 = 0.05
                            a750_a_899_99 = 0.045
                            a900_a_999_99 = 0.04
                            a1000_a_1499_99 = 0.035
                            a1500_a_1999_99 = 0.03
                            a2000_a_2499_99 = 0.03
                            a2500_a_2999_99 = 0.03
                            maior_3000 = 0.03
                            continue
# --------------- if de faixas --------------- #
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

                        elif vetor['FabricanteCodigo'] == '916' or vetor['FabricanteCodigo'] == 916:
                            classificacao = PRO_LUC.PP_Faixa_Site

                        #print(classificacao)
# --------------- Calcular preço omni --------------- #
                        for cont in range(0,len(portais)):

                            info_portais = portais[cont]
                            name_portal = info_portais['nome']
                            classificacao = info_portais['classificacao']
                            comissao_portal = info_portais['comissao']
                            ID_catalogo_portal = info_portais['ID_catalogo']
                            
                            #print("imposto",imposto,'\n',"comissao_portal",comissao_portal,'\n',"CustoAdmin",CustoAdmin,'\n',"classificacao",classificacao,'\n',)


                            somaPorc = imposto + comissao_portal + CustoAdmin + classificacao
                            resul_precopor = round(custo/(1-somaPorc))
                            resul_precopor = float(resul_precopor) + 0.99

                            if resul_precopor <= custo:
                                data_e_hora_atuais = datetime.now()
                                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                                name = 'Aviso Preco Inferior Omni '+name_portal+' | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                #print(name_portal,'Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(custo.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = estoqueatual)
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
                                name = 'Omni '+name_portal+' | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                print(name_portal,'Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(resul_precode.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = estoqueatual)

                            else:
                                data_e_hora_atuais = datetime.now()
                                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                                name = 'ERRO Omni '+name_portal+' | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                print('Erro ao atualizar',sku,name_portal)
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss, SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(resul_precode.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = estoqueatual)
# --------------- Calcula Preço Master ---------------
                        
                        try:
                            PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))
                            if PRO_LUC.PP_Classificao_total_absoluta == True:
                                a0_a_4_99 = float(faixa.PP_Classificao_total)
                                a0_a_4_99 = float(a0_a_4_99/100)

                                a5_a_14_99 = float(faixa.PP_Classificao_total)
                                a5_a_14_99 = float(a5_a_14_99/100)

                                a15_a_29_99 = float(faixa.PP_Classificao_total)
                                a15_a_29_99 = float(a15_a_29_99/100)
                                
                                a30_a_49_99 = float(faixa.PP_Classificao_total)
                                a30_a_49_99 = float(a30_a_49_99/100)

                                a50_a_79_99 = float(faixa.PP_Classificao_total)
                                a50_a_79_99 = float(a50_a_79_99/100)

                                a80_a_119_99 = float(faixa.PP_Classificao_total)
                                a80_a_119_99 = float(a80_a_119_99/100)

                                a120_a_149_99 = float(faixa.PP_Classificao_total)
                                a120_a_149_99 = float(a120_a_149_99/100)

                                a150_a_199_99 = float(faixa.PP_Classificao_total)
                                a150_a_199_99 = float(a150_a_199_99/100)

                                a200_a_249_99 = float(faixa.PP_Classificao_total)
                                a200_a_249_99 = float(a200_a_249_99/100)

                                a250_a_299_99 = float(faixa.PP_Classificao_total)
                                a250_a_299_99 = float(a250_a_299_99/100)

                                a300_a_349_99 = float(faixa.PP_Classificao_total)
                                a300_a_349_99 = float(a300_a_349_99/100)

                                a350_a_399_99 = float(faixa.PP_Classificao_total)
                                a350_a_399_99 = float(a350_a_399_99/100)

                                a400_a_449_99 = float(faixa.PP_Classificao_total)
                                a400_a_449_99 = float(a400_a_449_99/100)

                                a450_a_549_99 = float(faixa.PP_Classificao_total)
                                a450_a_549_99 = float(a450_a_549_99/100)

                                a550_a_649_99 = float(faixa.PP_Classificao_total)
                                a550_a_649_99 = float(a550_a_649_99/100)

                                a650_a_749_99 = float(faixa.PP_Classificao_total)
                                a650_a_749_99 = float(a650_a_749_99/100)

                                a750_a_899_99 = float(faixa.PP_Classificao_total)
                                a750_a_899_99 = float(a750_a_899_99/100)

                                a900_a_999_99 = float(faixa.PP_Classificao_total)
                                a900_a_999_99 = float(a900_a_999_99/100)

                                a1000_a_1499_99 = float(faixa.PP_Classificao_total)
                                a1000_a_1499_99 = float(a1000_a_1499_99/100)

                                a1500_a_1999_99 = float(faixa.PP_Classificao_total)
                                a1500_a_1999_99 = float(a1500_a_1999_99/100)

                                a2000_a_2499_99 = float(faixa.PP_Classificao_total)
                                a2000_a_2499_99 = float(a2000_a_2499_99/100)

                                a2500_a_2999_99 = float(faixa.PP_Classificao_total)
                                a2500_a_2999_99 = float(a2500_a_2999_99/100)

                                maior_3000 = float(faixa.PP_Classificao_total)
                                maior_3000 = float(maior_3000/100)

                            else:
                                try:
                                    faixa = Preco_Faixa.objects.get(PF_ID = '2')

                                    a0_a_4_99 = float(faixa.PF_0_a_4_99)
                                    a0_a_4_99 = float(a0_a_4_99/100)

                                    a5_a_14_99 = float(faixa.PF_5_a_14_99)
                                    a5_a_14_99 = float(a5_a_14_99/100)

                                    a15_a_29_99 = float(faixa.PF_15_a_29_99)
                                    a15_a_29_99 = float(a15_a_29_99/100)
                                    
                                    a30_a_49_99 = float(faixa.PF_30_a_49_99)
                                    a30_a_49_99 = float(a30_a_49_99/100)

                                    a50_a_79_99 = float(faixa.PF_50_a_79_99)
                                    a50_a_79_99 = float(a50_a_79_99/100)

                                    a80_a_119_99 = float(faixa.PF_80_a_119_99)
                                    a80_a_119_99 = float(a80_a_119_99/100)

                                    a120_a_149_99 = float(faixa.PF_120_a_149_99)
                                    a120_a_149_99 = float(a120_a_149_99/100)

                                    a150_a_199_99 = float(faixa.PF_150_a_199_99)
                                    a150_a_199_99 = float(a150_a_199_99/100)

                                    a200_a_249_99 = float(faixa.PF_200_a_249_99)
                                    a200_a_249_99 = float(a200_a_249_99/100)

                                    a250_a_299_99 = float(faixa.PF_250_a_299_99)
                                    a250_a_299_99 = float(a250_a_299_99/100)

                                    a300_a_349_99 = float(faixa.PF_300_a_349_99)
                                    a300_a_349_99 = float(a300_a_349_99/100)

                                    a350_a_399_99 = float(faixa.PF_350_a_399_99)
                                    a350_a_399_99 = float(a350_a_399_99/100)

                                    a400_a_449_99 = float(faixa.PF_400_a_449_99)
                                    a400_a_449_99 = float(a400_a_449_99/100)

                                    a450_a_549_99 = float(faixa.PF_450_a_549_99)
                                    a450_a_549_99 = float(a450_a_549_99/100)

                                    a550_a_649_99 = float(faixa.PF_550_a_649_99)
                                    a550_a_649_99 = float(a550_a_649_99/100)

                                    a650_a_749_99 = float(faixa.PF_650_a_749_99)
                                    a650_a_749_99 = float(a650_a_749_99/100)

                                    a750_a_899_99 = float(faixa.PF_750_a_899_99)
                                    a750_a_899_99 = float(a750_a_899_99/100)

                                    a900_a_999_99 = float(faixa.PF_900_a_999_99)
                                    a900_a_999_99 = float(a900_a_999_99/100)

                                    a1000_a_1499_99 = float(faixa.PF_1000_a_1499_99)
                                    a1000_a_1499_99 = float(a1000_a_1499_99/100)

                                    a1500_a_1999_99 = float(faixa.PF_1500_a_1999_99)
                                    a1500_a_1999_99 = float(a1500_a_1999_99/100)

                                    a2000_a_2499_99 = float(faixa.PF_2000_a_2499_99)
                                    a2000_a_2499_99 = float(a2000_a_2499_99/100)

                                    a2500_a_2999_99 = float(faixa.PF_2500_a_2999_99)
                                    a2500_a_2999_99 = float(a2500_a_2999_99/100)

                                    maior_3000 = float(faixa.PF_maior_3000)
                                    maior_3000 = float(maior_3000/100)

                                except:
                                    a0_a_4_99 = 0.30

                                    a5_a_14_99 = 0.15

                                    a15_a_29_99 = 0.10
                                    
                                    a30_a_49_99 = 0.08

                                    a50_a_79_99 = 0.07

                                    a80_a_119_99 = 0.05

                                    a120_a_149_99 = 0.03

                                    a150_a_199_99 = 0.03

                                    a200_a_249_99 = 0.03

                                    a250_a_299_99 = 0.03

                                    a300_a_349_99 = 0.03

                                    a350_a_399_99 = 0.03

                                    a400_a_449_99 = 0.03

                                    a450_a_549_99 = 0.03

                                    a550_a_649_99 = 0.03

                                    a650_a_749_99 = 0.03

                                    a750_a_899_99 = 0.03

                                    a900_a_999_99 = 0.02

                                    a1000_a_1499_99 = 0.01

                                    a1500_a_1999_99 = 0.01

                                    a2000_a_2499_99 = 0.01

                                    a2500_a_2999_99 = 0.01

                                    maior_3000 = 0.01

                        except:
                            a0_a_4_99 = 0.30

                            a5_a_14_99 = 0.15

                            a15_a_29_99 = 0.10
                            
                            a30_a_49_99 = 0.08

                            a50_a_79_99 = 0.07

                            a80_a_119_99 = 0.05

                            a120_a_149_99 = 0.03

                            a150_a_199_99 = 0.03

                            a200_a_249_99 = 0.03

                            a250_a_299_99 = 0.03

                            a300_a_349_99 = 0.03

                            a350_a_399_99 = 0.03

                            a400_a_449_99 = 0.03

                            a450_a_549_99 = 0.03

                            a550_a_649_99 = 0.03

                            a650_a_749_99 = 0.03

                            a750_a_899_99 = 0.03

                            a900_a_999_99 = 0.02

                            a1000_a_1499_99 = 0.01

                            a1500_a_1999_99 = 0.01

                            a2000_a_2499_99 = 0.01

                            a2500_a_2999_99 = 0.01

                            maior_3000 = 0.01

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
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            resul_precode = str(vetor['PrecoFicticioSite'])
                            resul_precopor = str(vetor['PrecoVenda'])
                            name = 'Master/Site Arrigo | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                            print('Master/Site Arrigo',str(vetor['Referencia']),'Não alterado!')
                            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = name_portal, SL_PrecoDe = float(resul_precode.replace(',','.')), SL_PrecoPor = float(resul_precopor.replace(',','.')), SL_Estoque = estoqueatual)

                            continue

                        #imposto
                        #CustoAdmin
                        #custo
                        #comissao

                        try:
                            PRO_LUC = get_object_or_404(Produto_Precificacao, pk = str(vetor['Codigo']))
                            comissao_portal = float(PRO_LUC.PP_Faixa_Site)/100
                            classificacao = float(PRO_LUC.PP_comissao_site)/100
                            CustoAdmin = float(PRO_LUC.CS_Custo_Adm_site)/100

                        except:
                            CustoAdmin = 0.14
                            comissao_portal = 0.1

                        somaPorc = imposto + comissao_portal + CustoAdmin + classificacao
                        #print('imposto',imposto,'\ncomissao_portal',comissao_portal,'\nCustoAdmin',CustoAdmin,'\nclassificacao',classificacao)
                        #print(custo)
                        resul_precopor = round(custo/(1-somaPorc))
                        resul_precopor = float(resul_precopor) + 0.90

                        if resul_precopor <= custo:
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            name = 'Aviso Preco Inferior Master '+name_portal+' | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                            print('Aviso Preco Inferior Master | Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                            prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Master', SL_PrecoDe = custo, SL_PrecoPor = resul_precopor, SL_Estoque = estoqueatual)
                            continue

                        if resul_precopor == float(vetor['PrecoVenda']) or resul_precopor == str(vetor['PrecoVenda']):
                            print('Master',str(vetor['Referencia']),"Não ouve mudança de preço!")
                            continue

                        else:
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
                            resul_precode = float(resul_precode + 0.90)
# --------------- Subir preço master ---------------

                            Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
                            headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
                            ip = str(Master.SC_ip) #Ip ou link da api

                            url = "http://"+ip+":2082/root/Preco/"+str(vetor['Codigo'])
                            try:
                                response = requests.request("GET", url, headers=headers)
                            except:
                                print("Sinc fechado erro ao obter informações da api!")
                                sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                sinc_open.SO_status = False
                                sinc_open.save()
                                return 0
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

                            printar = str(vetor['Referencia'])+ '\t'+ str(vetor['PrecoVenda'])+ '\t' + str(vetor['PrecoFicticioSite']) +'\t' +str(resul_precode)+ '\t' + str(resul_precopor) + '\n'
                            #arquivo = open(r'\\DESKTOP-U2IJQUL\Users\user\Desktop\GT2.0\sincronizador\resultado.txt','r')
                            #conteudo = arquivo.readlines()
                            #conteudo.append(printar)
                            #arquivo = open(r'\\DESKTOP-U2IJQUL\Users\user\Desktop\GT2.0\sincronizador\resultado.txt','w')
                            #arquivo.writelines(conteudo)
                            #arquivo.close()
                            

                            try:
                                #url = "http://"+ip+":2082/root/Preco/"+str(vetor['Codigo'])
                                #response = requests.request("put", url, headers=headers, data=json.dumps(preco))
                                #response = response.text.encode('utf8')
                                data_e_hora_atuais = datetime.now()
                                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                                name = 'Master Preço | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                print(vetor['Referencia'],'Master Preço | Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Master ", SL_PrecoDe = resul_precode, SL_PrecoPor = resul_precopor, SL_Estoque = estoqueatual)
                                #try:
                                #    url = "http://"+ip+":2082/root/produto/" + str(codigo) + "/fila"
                                #    response = requests.request("POST", url, headers=headers)
                                #    print('Master Preço | Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                                #except:
                                #    print('Não enviado sinc, Master Preço | Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')

                            except:
                                data_e_hora_atuais = datetime.now()
                                data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                                name = 'Erro Master Preço | '+str(vetor['Referencia'])+' | '+str(data_e_hora_em_texto)
                                print(vetor['Referencia'],'Erro Master Preço | Preco de:',resul_precode,'| Preco por:',resul_precopor,'OK')
                                prodss = Produto.objects.get(Pro_Id = vetor['Codigo'])
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = "Master ", SL_PrecoDe = resul_precode, SL_PrecoPor = resul_precopor, SL_Estoque = estoqueatual)
# --------------- Fim produtos ---------------
                    else:
                        continue
# --------------- Else de sem produtos--------------- #

        else:
            print('Sem Produtos para Integrar!\nIntegrando Vendas')

            for _ in iter(int, 1):
                url = "http://"+ip+":2082/root/venda"
                try:
                    response = requests.request("GET", url, headers=headers)
                except:
                    print("Sinc fechado erro ao obter informações da api!")
                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                    sinc_open.SO_status = False
                    sinc_open.save()
                    return 0
                response = response.text.encode('utf8')
                pedidos = json.loads(response)
                pedidos = pedidos['venda']
                if len(pedidos) <= 0:
# --------------- Inicio de Estoque --------------- #
                    print('Sem Venda para Integrar!\nIntegrando Estoque!')
                    url = "http://"+ip+":2082/root/estoque/"
                    try:
                        response = requests.request("GET", url, headers=headers)
                    except:
                        print("Sinc fechado erro ao obter informações da api!")
                        sinc_open  = get_object_or_404(Sinc_open, pk='1')
                        sinc_open.SO_status = False
                        sinc_open.save()
                        return 0
                    response = response.text.encode('utf8')
                    estoque = json.loads(response)
                    estoque = estoque['estoque']
                    if str(estoque) == '[]' or len(estoque) <= 0:
                        print('Sem Estoque para Integrar!')
# --------------- Integrar fornecedor --------------- #
                        url = "http://"+ip+":2082/root/fornecedor/"
                        try:
                            response = requests.request("GET", url, headers=headers)
                        except:
                            print("Sinc fechado erro ao obter informações da api!")
                            sinc_open  = get_object_or_404(Sinc_open, pk='1')
                            sinc_open.SO_status = False
                            sinc_open.save()
                            return 0
                        response = response.text.encode('utf8')
                        fornecedor = json.loads(response)
                        fornecedor = fornecedor['fornecedor']
                        if len(fornecedor) <= 0:
                            print('Sem Fornecedor para Integrar!')
                            sinc_open  = get_object_or_404(Sinc_open, pk='1')
                            sinc_open.SO_status = False
                            sinc_open.save()
                            return 0
                        else:
                            print('Integrando Fornecedores!')
                            n = 0
                            for n in range(0,len(fornecedor)):
                                id_fn =  fornecedor[n]['Codigo']
                                nome = fornecedor[n]['Nome']
                                try:
                                    forne = Fornecedores.objects.get(FN_ID = id_fn)
                                    forne.FN_Nome = nome
                                    forne.save()
                                except Fornecedores.DoesNotExist:
                                    forne = Fornecedores.objects.create(FN_ID = id_fn, FN_Nome= nome)   

                                url = "http://"+ip+":2082/root/fornecedor/"+str(id_fn)+"/ok"
                                try:
                                    response = requests.request("POST", url, headers=headers)
                                except:
                                    print("Sinc fechado erro ao obter informações da api!")
                                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                    sinc_open.SO_status = False
                                    sinc_open.save()
                                    return 0
# --------------- Estoque --------------- #
                    else:
                        for n in range(0,len(estoque)):
                            estoqueloja = 0
                            estoquebarracao = 0
                            estoqueatual = 0
                            prod = estoque[n]
                            estoqueatual = float(prod['EstoqueAtual'])
                            estoqueatual = int(estoqueatual)
                            codigo = prod['Codigo']
                            try:
                                prod2 = prod['MultiEstoque']
                                for nn in range(0,len(prod2)):
                                    vetor2 = prod2[nn]
                                    local = vetor2['Localizacao']
                                    local = local['Nome']
                                    if local == 'LOJA':
                                        estoqueloja = float(vetor2['Saldo'])
                                        estoqueloja = int(estoqueloja)
                                    elif local == 'BARRACÃO':
                                        estoquebarracao = float(vetor2['Saldo'])
                                        estoquebarracao = int(estoquebarracao)
                            except:
                                estoquebarracao = float(prod['EstoqueSite'])
                                estoquebarracao = int(estoquebarracao)
                            
                            data_e_hora_atuais = datetime.now()
                            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                            try:
                                prodss = Produto.objects.get(Pro_Id =codigo)
                                prodss.Pro_EstoqueBarracao = estoquebarracao
                                prodss.Pro_Loja = estoqueloja
                                prodss.Pro_EstoqueTotal = estoqueatual
                                name = 'Master Estoque | '+str(prodss.Pro_Sku)+' | '+str(data_e_hora_em_texto)
                                prodss = Produto.objects.get(Pro_Id = codigo)
                                sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = prodss.Pro_PrecoVenda, SL_PrecoPor = prodss.Pro_PrecoFicticio, SL_Estoque = estoqueatual)
                                print(n,codigo,'Update no banco!')	

                            except:
                                url = "http://"+ip+":2082/root/produto/" + str(codigo) + "/fila"
                                try:
                                    response = requests.request("POST", url, headers=headers)
                                except:
                                    print("Sinc fechado erro ao obter informações da api!")
                                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                    sinc_open.SO_status = False
                                    sinc_open.save()
                                    return 0
                                print(n,codigo,'Produto não cadastrado, adicionado a fila para integração!')
                                url = "http://"+ip+":2082/root/estoque/" + str(prod['Codigo']) + "/ok"
                                try:
                                    response = requests.request("POST", url, headers=headers)
                                except:
                                    print("Sinc fechado erro ao obter informações da api!")
                                    sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                    sinc_open.SO_status = False
                                    sinc_open.save()
                                    return 0
                                
                            try:
                                url = "http://"+ip+":2082/root/estoque/" + str(prod['Codigo']) + "/ok"
                                response = requests.request("POST", url, headers=headers)
                            except:
                                print("Sinc fechado erro ao obter informações da api!")
                                sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                sinc_open.SO_status = False
                                sinc_open.save()
                                return 0
                                print('Erro')
                else: 
# --------------- Inicio de Vendas--------------- #                     
                    for n in range(0,len(pedidos)):

                        vetor = pedidos[n]

                        data_e_hora_atuais = datetime.now()
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')

                        name = 'Master Pedido | '+str(vetor['Codigo'])+' | '+str(data_e_hora_em_texto)
                        
                        
                        try:
                            v = get_object_or_404(Venda, pk= vetor['Codigo'])
                            #v = Venda.objects.get(VE_Codigo = vetor['Codigo'])
                            v.VE_Codigo = vetor['Codigo']

                            v.VE_ClienteCodigo = vetor['ClienteCodigo']
                            v.VE_ClienteTipoPessoa = vetor['ClienteTipoPessoa']
                            v.VE_ClienteDocumento = vetor['ClienteDocumento']
                            v.VE_ClienteIdentidade = vetor['ClienteIdentidade']
                            v.VE_TransportadoraCodigo = vetor['TransportadoraCodigo']
                            v.VE_ValorTotal = vetor['ValorTotal']
                            v.VE_ValorFrete = vetor['ValorFrete']
                            v.VE_ValorEncargos = vetor['ValorEncargos']
                            v.VE_ValorDesconto = vetor['ValorDesconto']
                            v.VE_ValorComissao = vetor['ValorComissao']
                            v.VE_DataVenda = vetor['DataVenda']
                            v.VE_DataPagamento = vetor['DataPagamento']
                            v.VE_Entrega = vetor['Entrega']
                            v.VE_EntregaNome = vetor['EntregaNome']
                            v.VE_EntregaEmail = vetor['EntregaEmail']
                            v.VE_NumeroObjeto = vetor['NumeroObjeto']
                            v.VE_EntregaTelefone = vetor['EntregaTelefone']
                            v.VE_EntregaLogradouro = vetor['EntregaLogradouro']
                            v.VE_EntregaLogradouroNumero = vetor['EntregaLogradouroNumero']
                            v.VE_EntregaLogradouroComplemento = vetor['EntregaLogradouroComplemento']
                            v.VE_EntregaBairro = vetor['EntregaBairro']
                            v.VE_EntregaMunicipioNome = vetor['EntregaMunicipioNome']
                            v.VE_EntregaUnidadeFederativa = vetor['EntregaUnidadeFederativa']
                            v.VE_EntregaCEP = vetor['EntregaCEP']
                            v.VE_CupomDescontoCodigo = vetor['CupomDescontoCodigo']
                            v.VE_CupomDescontoValor = vetor['CupomDescontoValor']
                            v.VE_Observacoes = vetor['Observacoes']
                            v.VE_ObservacoesLoja = vetor['ObservacoesLoja']
                            v.VE_CodigoStatus = vetor['CodigoStatus']
                            v.VE_DescricaoStatus = vetor['DescricaoStatus']
                            v.VE_DataHoraStatus = vetor['DataHoraStatus']
                            v.VE_StatusID = vetor['StatusID']
                            v.VE_NotificarCliente = vetor['NotificarCliente']
                            v.VE_PrevisaoEntrega = vetor['PrevisaoEntrega']
                            v.VE_OrigemPedido = vetor['OrigemPedido']
                            v.VE_OrigemExterno = vetor['OrigemExterno']
                            v.VE_CodigoPedidoExterno = vetor['CodigoPedidoExterno']
                            v.VE_CodigoPedido = vetor['CodigoPedido']
                            v.VE_CodigoNotaFiscal = vetor['CodigoNotaFiscal']
                            v.VE_DataEntrega = vetor['DataEntrega']
                            v.VE_Empresa = vetor['Empresa']
                            v.VE_OrcamentoImpresso = vetor['OrcamentoImpresso']
                            v.VE_ValorTotalBruto = vetor['ValorTotalBruto']
                            v.VE_Orcamento = vetor['Orcamento']
                            v.VE_TipoVenda = vetor['TipoVenda']
                            v.VE_ClienteNome = vetor['ClienteNome']
                            v.VE_HoraVenda = vetor['HoraVenda']
                            v.VE_Origem = vetor['Origem']
                            v.VE_Cancelada = vetor['Cancelada']
                            v.VE_EnviarEmail = vetor['EnviarEmail']
                            v.VE_Reservada = vetor['Reservada']
                            v.VE_VendaPagamentos = vetor['VendaPagamentos']
                            v.VE_Itens = vetor['Itens']
                            v.VE_PesoLiquido = vetor['PesoLiquido']
                            v.VE_Status = vetor['Status']
                            v.VE_ClienteTipoDesconto = vetor['ClienteTipoDesconto']
                            v.VE_ClienteDesconto = vetor['ClienteDesconto']
                            v.VE_FormaParcelamentoCodigo = vetor['FormaParcelamentoCodigo']
                            v.VE_TransportadoraNome = vetor['TransportadoraNome']
                            v.VE_Parcelas = vetor['Parcelas']
                            v.VE_DataCancelamento = vetor['DataCancelamento']
                            v.VE_ClienteCodigoAnterior = vetor['ClienteCodigoAnterior']
                            v.VE_DataEnvio = vetor['DataEnvio']
                            v.VE_HoraEnvio = vetor['HoraEnvio']
                            v.VE_PacoteID = vetor['PacoteID']
                            v.VE_Pacotes = vetor['Pacotes']
                            v.VE_NotaFiscalNumero = vetor['NotaFiscalNumero']
                            v.VE_Danfe = vetor['Danfe']
                            v.VE_PrevisaoEntregaEmDias = vetor['PrevisaoEntregaEmDias']
                            v.VE_Conferido = vetor['Conferido']
                            v.VE_UsuarioConferencia = vetor['UsuarioConferencia']
                            v.VE_NumeroObjetoGeradoPeloSite = vetor['NumeroObjetoGeradoPeloSite']
                            v.VE_NFImpressa = vetor['NFImpressa']
                            v.VE_PrevisaoEnvio = vetor['PrevisaoEnvio']
                            v.VE_TransportadoraCodigoAnterior = vetor['TransportadoraCodigoAnterior']
                            v.VE_FreteSimulado = vetor['FreteSimulado']
                            v.VE_TipoDeCalculoDeFrete = vetor['TipoDeCalculoDeFrete']
                            v.VE_DataColeta = vetor['DataColeta']
                            v.VE_TransportadoraMuirCodigo = vetor['TransportadoraMuirCodigo']
                            v.VE_EmbalagemId = vetor['EmbalagemId']
                            v.VE_NotaCupom = vetor['NotaCupom']
                            v.VE_ECFSerie = vetor['ECFSerie']
                            v.VE_ECFNumero = vetor['ECFNumero']
                            v.VE_Volumes = vetor['Volumes']
                            v.VE_CodigoIntermediador = vetor['CodigoIntermediador']
                            v.VE_CNPJIntermediador = vetor['CNPJIntermediador']
                            v.VE_CNPJIntermediadorPagamento = vetor['CNPJIntermediadorPagamento']
                            v.VE_IdentificadorIntermediador = vetor['IdentificadorIntermediador']
                            v.VE_MuirIntegracao = vetor['MuirIntegracao']
                            v.VE_ChaveUnica = vetor['ChaveUnica']
                            v.VE_EntregaMunicipio = vetor['EntregaMunicipio']
                            v.VE_FormasDePagamento = vetor['FormasDePagamento']
                            v.save()

                            print(n,vetor['Codigo'],'Update no banco!')	

                            itens = vetor['Itens']
                            itens = itens[0]
                            code = itens['ProdutoCodigo']
                            preco = float(itens['PrecoUnitarioVenda'])
                            Quantidade = float(itens['Quantidade'])
                            Quantidade = int(Quantidade)
                            prodss = Produto.objects.get(Pro_Id = code)
                            sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = preco, SL_PrecoPor = preco, SL_Estoque = Quantidade)

                        except:
                            try:
                                NaoPersistir = vetor['NaoPersistir']
                            except:
                                NaoPersistir = False
                            Venda(VE_Codigo = vetor['Codigo'], VE_NaoPersistir = NaoPersistir, VE_ClienteCodigo = vetor['ClienteCodigo'], VE_ClienteTipoPessoa = vetor['ClienteTipoPessoa'], VE_ClienteDocumento = vetor['ClienteDocumento'], VE_ClienteIdentidade = vetor['ClienteIdentidade'], VE_TransportadoraCodigo = vetor['TransportadoraCodigo'], VE_ValorTotal = vetor['ValorTotal'], VE_ValorFrete = vetor['ValorFrete'], VE_ValorEncargos = vetor['ValorEncargos'], VE_ValorDesconto = vetor['ValorDesconto'], VE_ValorComissao = vetor['ValorComissao'], VE_DataVenda = vetor['DataVenda'], VE_DataPagamento = vetor['DataPagamento'], VE_Entrega = vetor['Entrega'], VE_EntregaNome = vetor['EntregaNome'], VE_EntregaEmail = vetor['EntregaEmail'], VE_NumeroObjeto = vetor['NumeroObjeto'], VE_EntregaTelefone = vetor['EntregaTelefone'], VE_EntregaLogradouro = vetor['EntregaLogradouro'], VE_EntregaLogradouroNumero = vetor['EntregaLogradouroNumero'], VE_EntregaLogradouroComplemento = vetor['EntregaLogradouroComplemento'], VE_EntregaBairro = vetor['EntregaBairro'], VE_EntregaMunicipioNome = vetor['EntregaMunicipioNome'], VE_EntregaUnidadeFederativa = vetor['EntregaUnidadeFederativa'], VE_EntregaCEP = vetor['EntregaCEP'], VE_CupomDescontoCodigo = vetor['CupomDescontoCodigo'], VE_CupomDescontoValor = vetor['CupomDescontoValor'], VE_Observacoes = vetor['Observacoes'], VE_ObservacoesLoja = vetor['ObservacoesLoja'], VE_CodigoStatus = vetor['CodigoStatus'], VE_DescricaoStatus = vetor['DescricaoStatus'], VE_DataHoraStatus = vetor['DataHoraStatus'], VE_StatusID = vetor['StatusID'], VE_NotificarCliente = vetor['NotificarCliente'], VE_PrevisaoEntrega = vetor['PrevisaoEntrega'], VE_OrigemPedido = vetor['OrigemPedido'], VE_OrigemExterno = vetor['OrigemExterno'], VE_CodigoPedidoExterno = vetor['CodigoPedidoExterno'], VE_CodigoPedido = vetor['CodigoPedido'], VE_CodigoNotaFiscal = vetor['CodigoNotaFiscal'], VE_DataEntrega = vetor['DataEntrega'], VE_Empresa = vetor['Empresa'], VE_OrcamentoImpresso = vetor['OrcamentoImpresso'], VE_ValorTotalBruto = vetor['ValorTotalBruto'], VE_Orcamento = vetor['Orcamento'], VE_TipoVenda = vetor['TipoVenda'], VE_ClienteNome = vetor['ClienteNome'], VE_HoraVenda = vetor['HoraVenda'], VE_Origem = vetor['Origem'], VE_Cancelada = vetor['Cancelada'], VE_EnviarEmail = vetor['EnviarEmail'], VE_Reservada = vetor['Reservada'], VE_VendaPagamentos = vetor['VendaPagamentos'], VE_Itens = vetor['Itens'], VE_PesoLiquido = vetor['PesoLiquido'], VE_Status = vetor['Status'], VE_ClienteTipoDesconto = vetor['ClienteTipoDesconto'], VE_ClienteDesconto = vetor['ClienteDesconto'], VE_FormaParcelamentoCodigo = vetor['FormaParcelamentoCodigo'], VE_TransportadoraNome = vetor['TransportadoraNome'], VE_Parcelas = vetor['Parcelas'], VE_DataCancelamento = vetor['DataCancelamento'], VE_ClienteCodigoAnterior = vetor['ClienteCodigoAnterior'], VE_DataEnvio = vetor['DataEnvio'], VE_HoraEnvio = vetor['HoraEnvio'], VE_PacoteID = vetor['PacoteID'], VE_Pacotes = vetor['Pacotes'], VE_NotaFiscalNumero = vetor['NotaFiscalNumero'], VE_Danfe = vetor['Danfe'], VE_PrevisaoEntregaEmDias = vetor['PrevisaoEntregaEmDias'], VE_Conferido = vetor['Conferido'], VE_UsuarioConferencia = vetor['UsuarioConferencia'], VE_NumeroObjetoGeradoPeloSite = vetor['NumeroObjetoGeradoPeloSite'], VE_NFImpressa = vetor['NFImpressa'], VE_PrevisaoEnvio = vetor['PrevisaoEnvio'], VE_TransportadoraCodigoAnterior = vetor['TransportadoraCodigoAnterior'], VE_FreteSimulado = vetor['FreteSimulado'], VE_TipoDeCalculoDeFrete = vetor['TipoDeCalculoDeFrete'], VE_DataColeta = vetor['DataColeta'], VE_TransportadoraMuirCodigo = vetor['TransportadoraMuirCodigo'], VE_EmbalagemId = vetor['EmbalagemId'], VE_NotaCupom = vetor['NotaCupom'], VE_ECFSerie = vetor['ECFSerie'], VE_ECFNumero = vetor['ECFNumero'], VE_Volumes = vetor['Volumes'], VE_CodigoIntermediador = vetor['CodigoIntermediador'], VE_CNPJIntermediador = vetor['CNPJIntermediador'], VE_CNPJIntermediadorPagamento = vetor['CNPJIntermediadorPagamento'], VE_IdentificadorIntermediador = vetor['IdentificadorIntermediador'], VE_MuirIntegracao = vetor['MuirIntegracao'], VE_ChaveUnica = vetor['ChaveUnica'], VE_EntregaMunicipio = vetor['EntregaMunicipio'], VE_FormasDePagamento = vetor['FormasDePagamento']).save()
                            print(n,vetor['Codigo'],'cadastrado no banco!')	
                            itens = vetor['Itens']
                            itens = itens[0]
                            code = itens['ProdutoCodigo']
                            preco = float(itens['PrecoUnitarioVenda'])
                            Quantidade = float(itens['Quantidade'])
                            Quantidade = int(Quantidade)
                            #prodss = Produto.objects.get(Pro_Id = code)
                            #sinc = Sinc_log.objects.create(SL_Nome = name, SL_user = "API", SL_ProdutoID = prodss,SL_view = False, SL_GetOrigem = 'API Aplicação', SL_PostSaida = 'Não enviado', SL_PrecoDe = preco, SL_PrecoPor = preco, SL_Estoque = Quantidade)
                        
                        try:
                            url = "http://"+ip+":2082/root/venda/"+str(vetor['Codigo'])+"/ok"
                            try:
                                response = requests.request("POST", url, headers=headers)
                            except:
                                print("Sinc fechado erro ao obter informações da api!")
                                sinc_open  = get_object_or_404(Sinc_open, pk='1')
                                sinc_open.SO_status = False
                                sinc_open.save()
                                return 0
                            response = response.text.encode('utf8')
                        except:
                            print("Sinc fechado erro ao obter informações da api!")
                            sinc_open  = get_object_or_404(Sinc_open, pk='1')
                            sinc_open.SO_status = False
                            sinc_open.save()
                            return 0
                            print("Erro ao dar ok na fila do pedido:",vetor['Codigo'])

        tempo = int(Master.SC_TempoExecucao)
        sleep(tempo)

    #except:
    #    sinc_open  = get_object_or_404(Sinc_open, pk='1')
    #    sinc_open.SO_status = False
    #    sinc_open.save()

    sinc_open  = get_object_or_404(Sinc_open, pk='1')
    sinc_open.SO_status = False
    sinc_open.save()


@login_required
def sinc(request):
    skus = {}
    setor = request.user.Us_Setor
    if setor == "sinc" or setor == "ti" or setor == "administracao":
        #sincdata = get_object_or_404(Sinc_Config, pk=1)
        #print(sincdata.SA_Senha)
        #senha_sinc = sincdata.SA_Senha ==
        #usuario_sinc = sincdata.SA_Nome
        #if request.method == 'POST':
        #    senha = request.POST.get('senha')
        #    usuario = request.POST.get('user')
        #    if senha_sinc == senha and usuario_sinc == usuario:
        sinc_open  = get_object_or_404(Sinc_open, pk='1')
        if sinc_open.SO_status == True:
            log = Sinc_log.objects.filter(SL_view=False)
            pesq = get_object_or_404(Sinc_view, pk='1')
            pesq_omni = pesq.SV_Omni
            for n in range(0,len(log)):
                log[n].SL_view = True
                log[n].save()
            return render(request,'aviso.html',{'logs':log})
        else:
            start_sinc.now()
            return render(request,'Sinc.html')
        #    else:
        #        return render(request,'home.html',{'aviso':'Senha ou Usuario incorreto!'})

    else:
        sinc_open  = get_object_or_404(Sinc_open, pk='1')
        if sinc_open.SO_status == True:
            log = Sinc_log.objects.filter(SL_view=False)
            pesq = get_object_or_404(Sinc_view, pk='1')
            pesq_omni = pesq.SV_Omni
            for n in range(0,len(log)):
                log[n].SL_view = True
                log[n].save()

            return render(request,'aviso.html',{'logs':log})
        else:

            return HttpResponse("<h1>Sem acesso ao Sinc</h1>")


@login_required
def home(request):
    start_sinc.now()
    return render(request,'home.html')


@login_required
def teste(request):
    #Produto
    codigo = 14501

    try:
        prodss = Produto.objects.get(Pro_Id = codigo)
    except:
        Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
        headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
        ip = str(Master.SC_ip) #Ip ou link da api
        url = "http://"+ip+":2082/root/produto/" + str(codigo) + "/fila"
        response = requests.request("POST", url, headers=headers)
        print(codigo,'Produto não cadastrado, adicionado a fila para integração!')
        return render(request,'home.html')

    custo = float(prodss.Pro_PrecoCusto)
    prateleira_produto = prodss.Pro_LocalizacaoSetor

    #Faixa valida
    try:
        faixa = Preco_Faixa.objects.get(PF_None = prateleira_produto)
    except:
        faixa = '?'

    #Obter Faixas
    imposto = Preco.objects.get(PR_ID = 1)
    imposto = imposto.PR_Valor
    imposto = str(imposto).replace('.','')
    imposto = '0.'+imposto
    imposto = float(imposto)

    CustoAdm = Preco.objects.get(PR_ID = 2)
    CustoAdm = CustoAdm.PR_Valor
    CustoAdm = str(CustoAdm).replace('.','')
    CustoAdm = '0.'+ CustoAdm
    CustoAdm = float(CustoAdm)

    intermediador = Preco.objects.get(PR_ID = 3)
    intermediador = intermediador.PR_Valor
    intermediador = str(intermediador).replace('.','')
    intermediador = '0.'+ intermediador
    intermediador = float(intermediador)

    integrador = Preco.objects.get(PR_ID = 4)
    integrador = integrador.PR_Valor
    integrador = str(integrador).replace('.','')
    integrador = '0.'+ integrador
    integrador = float(integrador)

    comissao = intermediador + integrador
    comissao = str(comissao).replace('.','')
    comissao = '0.'+ comissao
    comissao = float(comissao)
    
    print('\nimposto:',imposto,'\nCustoAdm:',CustoAdm,'\ncomissao:',comissao)
    
    #Obter classificação
    if faixa == '?':
        classificacao = 15
    if faixa == 'Absoluto':
        classificacao = prodss.Pro_LocalizacaoBox
    else:
        if custo <= 4.99:
            classificacao = faixa.PF_0_a_4_99
        elif custo >= 5 and custo <= 14.99:
            classificacao = faixa.PF_5_a_14_99
        elif custo >= 15 and custo <= 29.99:
            classificacao = faixa.PF_15_a_29_99
        elif custo >= 30 and custo <= 49.99:
            classificacao = faixa.PF_30_a_49_99
        elif custo >= 50 and custo <= 79.99:
            classificacao = faixa.PF_50_a_79_99
        elif custo >= 80 and custo <= 119.99:
            classificacao = faixa.PF_80_a_119_99
        elif custo >= 120 and custo <= 149.99:
            classificacao = faixa.PF_120_a_149_99
        elif custo >= 150 and custo <= 199.99:
            classificacao = faixa.PF_150_a_199_99
        elif custo >= 200 and custo <= 249.99:
            classificacao = faixa.PF_200_a_249_99
        elif custo >= 250 and custo <= 299.99:
            classificacao = faixa.PF_250_a_299_99
        elif custo >= 300 and custo <= 349.99:
            classificacao = faixa.PF_300_a_349_99
        elif custo >= 350 and custo <= 399.99:
            classificacao = faixa.PF_350_a_399_99
        elif custo >= 400 and custo <= 449.99:
            classificacao = faixa.PF_400_a_449_99
        elif custo >= 450 and custo <= 549.99:
            classificacao = faixa.PF_450_a_549_99
        elif custo >= 550 and custo <= 649.99:
            classificacao = faixa.PF_550_a_649_99
        elif custo >= 650 and custo <= 749.99:
            classificacao = faixa.PF_650_a_749_99
        elif custo >= 750 and custo <= 899.99:
            classificacao = faixa.PF_750_a_899_99
        elif custo >= 900 and custo <= 999.99:
            classificacao = faixa.PF_900_a_999_99
        elif custo >= 1000 and custo <= 1499.99:
            classificacao = faixa.PF_1000_a_1499_99
        elif custo >= 1500 and custo <= 1999.99:
            classificacao = faixa.PF_1500_a_1999_99
        elif custo >= 2000 and custo <= 2499.99:
            classificacao = faixa.PF_2000_a_2499_99
        elif custo >= 2500 and custo <= 2999.99:
            classificacao = faixa.PF_2500_a_2999_99
        elif custo >= 3000:
            classificacao = faixa.PF_maior_3000
        else:
            classificacao = faixa.PF_maior_3000

    #Converte Classificacao
    classificacao = str(classificacao).replace('.','')
    classificacao = '0.'+classificacao
    classificacao = float(classificacao)
    print('classificacao',classificacao)

    soma_porcent = classificacao + imposto + CustoAdm + comissao
    resul_precopor = round(custo/(1-soma_porcent))
    resul_precopor = float(resul_precopor) + 0.90

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
    resul_precode = float(resul_precode + 0.90)
    
    

    Master = get_object_or_404(Sinc_Config, pk='1') # è usada como um objeto que contem as infos do sinc e para nome
    headers = {'X-Token':str(Master.SC_Key)} #Token acesso api
    ip = str(Master.SC_ip) #Ip ou link da api

    url = "http://"+str(ip)+":2082/root/Preco/"+str(codigo)
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
        url = "http://"+str(ip)+":2082/root/Preco/"+str(codigo)
        response = requests.request("put", url, headers=headers, data=json.dumps(preco))
        response = response.text.encode('utf8')
    except:
        print('Erro ao salvar custos e preço!')

    return render(request,'home.html')