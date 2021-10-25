from django.db import models
from auditlog.registry import auditlog
from django.conf import settings
import jsonfield

from precos.models import Comissoes

# Create your models here.
class Produto(models.Model):
	Pro_Id = models.IntegerField(primary_key=True) # Codigo / até 15
	Pro_Sku = models.CharField(unique=True, max_length=50) # Referencia / até 15
	Pro_Nome = models.TextField() # Nome / 200
	Pro_Conferencia_loja = models.BooleanField(unique=False, null=True)
	Pro_EstoqueBarracao = models.TextField() # 'Obter em Estoque' / int
	Pro_Loja = models.TextField() # 'Obter em Estoque'/ int
	Pro_EstoqueTotal = models.TextField() # EstoqueAtual / int	
	Pro_Ean = models.TextField() # EAN / 12
	Pro_Ativo = models.TextField() # Ativo / 12
	Pro_LocalizacaoSetor = models.TextField() # LocalizacaoSetor / até 15
	Pro_LocalizacaoBox = models.TextField() # LocalizacaoBox / até 15
	Pro_SemEan = models.TextField() # SubstituirEANPorSemGTIN / boolean
	Pro_FornecedorCodigo = models.TextField() # FornecedorCodigo / int
	Pro_FabricanteCodigo = models.TextField() # FabricanteCodigo / int
	Pro_Classificacao = models.TextField() # Classificacao / até 15
	Pro_Modelo = models.TextField() # Modelo / até 15
	Pro_Conteudo = models.TextField() # Conteudo / até 15
	Pro_DescricaoCurta = models.TextField() # DescricaoCurta / até 250
	Pro_DescricaoLonga = models.TextField() # DescricaoLonga / infinito
	Pro_PrecoCusto = models.TextField() # PrecoCusto / float
	Pro_PrecoVenda = models.TextField() # PrecoVenda / float
	Pro_PrecoFicticio = models.TextField() # Pro_PrecoFicticio / float
	Pro_Altura = models.TextField() # Altura / float
	Pro_Largura = models.TextField() # Largura / float
	Pro_Profundidade = models.TextField() # Profundidade / float
	Pro_Peso = models.TextField() # Peso / float
	Pro_NCM = models.TextField() # NCM / int
	Pro_Composicao = models.TextField() # {{Composicao}} / infinito
	Pro_CategoriaPrincipal = models.TextField() # {{CategoriaPrincipal}} / infinito
	Pro_DisponibilidadeEmEstoque = models.TextField() # DisponibilidadeEmEstoque / int
	Pro_DisponibilidadeSemEstoque = models.TextField() # DisponibilidadeSemEstoque /int
	Pro_PromocaoInicio = models.TextField() # PromocaoInicio / date
	Pro_PromocaoFim = models.TextField() # PromocaoFim / date
	Pro_PrevalecerPrecoPai = models.TextField() # PrevalecerPrecoPai / boolean
	Pro_Taxa = models.TextField() # Taxa / float
	Pro_NumeroMaximoParcelas = models.TextField() # NumeroMaximoParcelas / int
	Pro_EstoqueMaximo = models.TextField() # EstoqueMaximo / int
	Pro_TipoDisponibilidade = models.TextField() # TipoDisponibilidade / int
	Pro_PreVenda = models.TextField() # PreVenda / boolean
	Pro_PreVendaData = models.TextField() # PreVendaData / date
	Pro_PreVendaLimite = models.TextField() # PreVendaLimite / date
	Pro_VendaSemEstoque = models.TextField() # VendaSemEstoque / boolean
	Pro_VendaSemEstoqueData = models.TextField() # VendaSemEstoqueData / date
	Pro_VendaSemEstoqueLimite = models.TextField() # VendaSemEstoqueLimite / date
	Pro_ExibirDisponibilidade = models.TextField() # ExibirDisponibilidade / boolean
	Pro_TipoReposicao = models.TextField() # TipoReposicao / infinito
	Pro_PesoCubico = models.TextField() # PesoCubico / float
	Pro_QuantidadeMaximaPorCliente = models.TextField() # QuantidadeMaximaPorCliente / int
	Pro_FreteGratis = models.TextField() # FreteGratis / boolean
	Pro_TituloVariacao = models.TextField() # TituloVariacao / ate 120
	Pro_TituloSubVariacao = models.TextField() # TituloSubVariacao / ate 120
	Pro_MetaTitle = models.TextField() # MetaTitle / ate 120
	Pro_MetaDescription = models.TextField() # MetaDescription / ate 250
	Pro_MetaKeywords = models.TextField() # MetaKeywords / infinito
	Pro_PalavrasParaPesquisa = models.TextField() # PalavrasParaPesquisa  / infitnito
	Pro_Ordem = models.TextField() # Ordem / int
	Pro_VisualizarUrlDireto = models.TextField() # VisualizarUrlDireto / boolean
	Pro_TemOpcaoPresente = models.TextField() # TemOpcaoPresente / boolean
	Pro_PresenteValor = models.TextField() # PresenteValor / float
	Pro_Video = models.TextField() # Video / ate 250
	Pro_UnidadeSigla = models.TextField() # UnidadeSigla / ate 10
	Pro_Foto = models.TextField() # Foto / infitimo
	Pro_ControlaEstoque = models.TextField() # ControlaEstoque / boolean
	Pro_Fornecedores = models.TextField() # {{Fornecedores}} / infinito
	Pro_Imagens = models.TextField() # Imagens / infinito
	Pro_CodigoPai = models.TextField() # CodigoPai / até 15
	Pro_EstoqueSite = models.TextField() # EstoqueSite / int
	Pro_Composto = models.TextField() # Composto / boolean
	Pro_Grade = jsonfield.JSONField(unique=False, null=True) # {{Grade}} / infinito
	Pro_QuantidadeTerceiros = models.TextField() # QuantidadeTerceiros / int
	Pro_CST = models.TextField() # CST / int
	Pro_NomeAbreviado = models.TextField() # NomeAbreviado / até 250
	Pro_IPICST = models.TextField() # IPICST / int
	Pro_PISCST = models.TextField() # PISCST / int
	Pro_COFINSCST = models.TextField() # COFINSCST / int
	Pro_PISAliquota = models.TextField() # PISAliquota / float
	Pro_COFINSAliquota = models.TextField() # COFINSAliquota / float
	Pro_CFOPCodigo = models.TextField() # CFOPCodigo / int
	Pro_ICMSTipo = models.TextField() # ICMSTipo / ate 15
	Pro_ICMSST = models.TextField() # ICMSST / float
	Pro_CSTOrigem = models.TextField() # CSTOrigem / int
	Pro_PrecoFicticioSite = models.TextField() # PrecoFicticioSite / float
	Pro_PrecoSite = models.TextField() # PrecoSite / float
	Pro_ICMSVenda = models.TextField() # ICMSVenda / float
	Pro_Volume = models.TextField() # Volume / int
	Pro_ItensInclusos = models.TextField() # ItensInclusos / ate 250
	Pro_DadosTecnicos = models.TextField() # DadosTecnicos / ate 250
	Pro_Categorias = models.TextField() # {{Categorias}} / infinito
	Pro_Unidade = models.TextField() # {{Unidade}} / infinito
	Pro_Thumbnail = models.TextField() # Thumbnail / ate 250
	Pro_EnviarSite = models.TextField() # EnviarSite / boolean
	Pro_Comissao = models.TextField() # Comissao / float
	Pro_ExibeEsgotado = models.TextField() # ExibeEsgotado / boolean
	Pro_CSOSN = models.TextField() # CSOSN / int
	Pro_CEST = models.TextField() # CEST / ate 250
	Pro_ICMSCompraAliquota = models.TextField() # ICMSCompraAliquota / float
	Pro_ICMSSTBase = models.TextField() # ICMSSTBase / float
	Pro_ICMSReducaoBaseCalculo = models.TextField() # ICMSReducaoBaseCalculo / float
	Pro_ICMSBase = models.TextField() # ICMSBase / float
	Pro_IPIAliquota = models.TextField() # IPIAliquota / float
	Pro_IPICompraAliquota = models.TextField() # IPICompraAliquota / float
	Pro_ISSAliquota = models.TextField() # ISSAliquota / float
	Pro_ISSCSERV = models.TextField() # ISSCSERV / ate 250
	Pro_Lista = models.TextField() # Lista / ate 250
	Pro_GrupoTributacao = models.TextField() # GrupoTributacao / int
	Pro_DefinicaoPrecoEscopo = models.TextField() # DefinicaoPrecoEscopo / ate 15
	Pro_VtexLojasId = models.TextField() # VtexLojasId / ate 15
	Pro_DefinicaoProdutoCodigo = models.TextField() # DefinicaoProdutoCodigo / int
	Pro_Slug = models.TextField() # Slug / ate 250
	Pro_AtrelamentoDescricao = models.TextField() # AtrelamentoDescricao / ate 250
	Pro_BeneficiosDescricao = models.TextField() # BeneficiosDescricao / ate 250
	Pro_DestaqueDescricao = models.TextField() # DestaqueDescricao / ate 250
	Pro_PromocaoDescricao = models.TextField() # PromocaoDescricao / ate 250
	Pro_GanheBrindeDescricao = models.TextField() # GanheBrindeDescricao / ate 250
	Pro_LancamentoDescricao = models.TextField() # LancamentoDescricao / ate 250
	Pro_MedidasDescricao = models.TextField() # MedidasDescricao / ate 250
	Pro_QuemUsaDescricao = models.TextField() # QuemUsaDescricao / ate 250
	Pro_SeguroDescricao = models.TextField() # SeguroDescricao / ate 250
	Pro_SugestaoDeUsoDescricao = models.TextField() # SugestaoDeUsoDescricao / ate 250
	Pro_PercentualMarkupPrecoMargem = models.TextField() # PercentualMarkupPrecoMargem / float
	Pro_PrecoPercentual = models.TextField() # PrecoPercentual / float
	Pro_PrevalecerPromoPai = models.TextField() # PrevalecerPromoPai / boolean
	Pro_PontosFidelidade = models.TextField() # PontosFidelidade / int
	Pro_SemEntregas = models.TextField() # SemEntregas / boolean
	Pro_ExibirNovo = models.TextField() # ExibirNovo / ate 15
	Pro_ExibirNovoInicio = models.TextField() # ExibirNovoInicio / date
	Pro_ExibirNovoFim = models.TextField() # ExibirNovoFim / date
	Pro_EstoqueMinimoIndisponibilizar = models.TextField() # EstoqueMinimoIndisponibilizar / ate 15
	Pro_EstoqueMinimoNotificar = models.TextField() # EstoqueMinimoNotificar / ate 15
	Pro_ExibirProdutoInicio = models.TextField() # ExibirProdutoInicio / date
	Pro_ExibirProdutoFim = models.TextField() # ExibirProdutoFim / date
	Pro_CoreExibirPreco = models.TextField() # CoreExibirPreco / ate 250
	Pro_BundleOpcao = models.TextField() # {{BundleOpcao}} / infinito
	Pro_Flag = models.TextField() # {{Flag}} / infinito
	Pro_Acabamento = models.TextField() # Acabamento / ate 250
	Pro_AnoPublicacao = models.TextField() # AnoPublicacao / ate 250
	Pro_Assunto = models.TextField() # Assunto / ate 250
	Pro_Autor = models.TextField() # Autor / ate 250
	Pro_Colecao = models.TextField() # Colecao / ate 250
	Pro_Edicao = models.TextField() # Edicao / ate 250
	Pro_Editora = models.TextField() # Editora / ate 250
	Pro_Formato = models.TextField() # Formato / ate 250
	Pro_Idioma = models.TextField() # Idioma / ate 250
	Pro_ISBN = models.TextField() # ISBN / ate 250
	Pro_ISBN13 = models.TextField() # ISBN13 / ate 250
	Pro_Pagina = models.TextField() # Pagina / ate 250
	Pro_Titulo = models.TextField() # Titulo / ate 250
	Pro_Tradutor = models.TextField() # Tradutor / ate 250
	Pro_CamposRelacionaveis = models.TextField() # {{CamposRelacionaveis}} / infinito
	Pro_Editor = models.TextField() # Editor / ate 250
	Pro_Ilustrador = models.TextField() # Ilustrador / ate 250
	Pro_Organizador = models.TextField() # Organizador / ate 250
	Pro_Fotografo = models.TextField() # Fotografo / ate 250
	Pro_PaisOrigem = models.TextField() # PaisOrigem / ate 250
	Pro_DataPublicacao = models.TextField() # DataPublicacao / ate 250
	Pro_NVolume = models.TextField() # NVolume / ate 250
	Pro_EditaSinopse = models.TextField() # EditaSinopse / ate 250
	Pro_BarraExtra = models.TextField() # BarraExtra / ate 250
	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

	def __str__(self):
		return self.Pro_Sku


class Preco_Portal(models.Model):
	Pr_ID = models.ForeignKey(Produto, on_delete=models.CASCADE) # Codigo / até 15
	Pr_Sku = models.ForeignKey(Produto, to_field='Pro_Sku',related_name='+', on_delete=models.CASCADE) # Referencia / até 15
	Pr_Amazon_KES_De = models.FloatField()
	Pr_Amazon_KES_Por = models.FloatField()
	Pr_Amazon_KES_Absoluto = models.FloatField()
	Pr_B2W_GEA_De = models.FloatField()
	Pr_B2W_GEA_Por = models.FloatField()
	Pr_B2W_GEA_Absoluto = models.FloatField()
	Pr_B2W_JCMA_De = models.FloatField()
	Pr_B2W_JCMA_Por = models.FloatField()
	Pr_B2W_JCMA_Absoluto = models.FloatField()
	Pr_B2W_KC_De = models.FloatField()
	Pr_B2W_KC_Por = models.FloatField()
	Pr_B2W_KC_Absoluto = models.FloatField()
	Pr_Carrefour_ALK_De = models.FloatField()
	Pr_Carrefour_ALK_Por = models.FloatField()
	Pr_Carrefour_ALK_Absoluto = models.FloatField()
	Pr_Carrefour_GEA_De = models.FloatField()
	Pr_Carrefour_GEA_Por = models.FloatField()
	Pr_Carrefour_GEA_Absoluto = models.FloatField()
	Pr_Centauro_ALK_De = models.FloatField()
	Pr_Centauro_ALK_Por = models.FloatField()
	Pr_Centauro_ALK_Absoluto = models.FloatField()
	Pr_Cnova_KES_De = models.FloatField()
	Pr_Cnova_KES_Por = models.FloatField()
	Pr_Cnova_KES_Absoluto = models.FloatField()
	Pr_MadeiraMadeira_Kes_De = models.FloatField()
	Pr_MadeiraMadeira_Kes_Por = models.FloatField()
	Pr_MadeiraMadeira_Kes_Absoluto = models.FloatField()
	Pr_Magalu_GEA_De = models.FloatField()
	Pr_Magalu_GEA_Por = models.FloatField()
	Pr_Magalu_GEA_Absoluto = models.FloatField()
	Pr_Magalu_KC_De = models.FloatField()
	Pr_Magalu_KC_Por = models.FloatField()
	Pr_Magalu_KC_Absoluto = models.FloatField()
	Pr_Netshoes_ALK_De = models.FloatField()
	Pr_Netshoes_ALK_Por = models.FloatField()
	Pr_Netshoes_ALK_Absoluto = models.FloatField()
	Pr_Netshoes_KES_De = models.FloatField()
	Pr_Netshoes_KES_Por = models.FloatField()
	Pr_Netshoes_KES_Absoluto = models.FloatField()

	def __str__(self):
		return self.Pr_Sku


class Confere_Preco_log(models.Model):
	CP_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	CP_Sku = models.ForeignKey(Produto, on_delete=models.CASCADE)
	CP_nome = models.CharField(max_length=100,unique=False, null=True)
	CP_Data_atualizacao = models.CharField(max_length=100,unique=False, null=True)	
	CP_preco = models.FloatField(unique=False, null=True)
	CP_User = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

	def __str__(self):
		return self.CP_nome


class Produto_Precificacao(models.Model):
	PP_ID = models.IntegerField(primary_key=True) # Codigo / até 15
	PP_sku = models.ForeignKey(Produto, on_delete=models.CASCADE)
	PP_nome = models.CharField(max_length=100,unique=False, null=True)
	PP_estoque_fisico = models.IntegerField(unique=False, null=True)
	PP_fornecedor = models.CharField(max_length=100,unique=False, null=True)
	PP_custo = models.CharField(max_length=100,unique=False, null=True)

	PP_tipo_produto = models.CharField(max_length=30,unique=False, null=True)
	
	PP_custo_adm_portal = models.FloatField(unique=False, null=True)
	PP_custo_adm_site = models.FloatField(unique=False, null=True)
	PP_imposto = models.FloatField(unique=False, null=True)
	
	PP_Classificao_total_absoluta = models.BooleanField(unique=False, null=True)
	PP_Classificao_total = models.FloatField(unique=False, null=True)

	PP_Faixa_Site_absoluta = models.BooleanField(unique=False, null=True)
	PP_Faixa_Site = models.FloatField(unique=False, null=True)

	PP_Faixa_Portal_absoluta = models.BooleanField(unique=False, null=True)
	PP_Faixa_Portal = models.FloatField(unique=False, null=True)

	PP_comissao_site_absoluta = models.BooleanField(unique=False, null=True)
	PP_comissao_site = models.FloatField(unique=False, null=True)

	PP_Amazon_KES_absoluta = models.BooleanField(unique=False, null=True)
	PP_Amazon_KES = models.FloatField(unique=False, null=True)

	PP_B2W_ALK_absoluta = models.BooleanField(unique=False, null=True)
	PP_B2W_ALK = models.FloatField(unique=False, null=True)

	PP_B2W_GEA_absoluta = models.BooleanField(unique=False, null=True)
	PP_B2W_GEA = models.FloatField(unique=False, null=True)

	PP_B2W_JCMA_absoluta = models.BooleanField(unique=False, null=True)
	PP_B2W_JCMA = models.FloatField(unique=False, null=True)

	PP_B2W_KC_absoluta = models.BooleanField(unique=False, null=True)
	PP_B2W_KC = models.FloatField(unique=False, null=True)

	PP_Carrefour_ALK_absoluta = models.BooleanField(unique=False, null=True)
	PP_Carrefour_ALK = models.FloatField(unique=False, null=True)

	PP_Carrefour_GEA_absoluta = models.BooleanField(unique=False, null=True)
	PP_Carrefour_GEA = models.FloatField(unique=False, null=True)

	PP_Centauro_ALK_absoluta = models.BooleanField(unique=False, null=True)
	PP_Centauro_ALK = models.FloatField(unique=False, null=True)

	PP_Cnova_KES_absoluta = models.BooleanField(unique=False, null=True)
	PP_Cnova_KES = models.FloatField(unique=False, null=True)

	PP_MadeiraMadeira_KES_absoluta = models.BooleanField(unique=False, null=True)
	PP_MadeiraMadeira_KES = models.FloatField(unique=False, null=True)

	PP_Magalu_GEA_absoluta = models.BooleanField(unique=False, null=True)
	PP_Magalu_GEA = models.FloatField(unique=False, null=True)

	PP_Magalu_KC_absoluta = models.BooleanField(unique=False, null=True)
	PP_Magalu_KC = models.FloatField(unique=False, null=True)

	PP_Netshoes_KES_absoluta = models.BooleanField(unique=False, null=True)
	PP_Netshoes_KES = models.FloatField(unique=False, null=True)

	PP_Netshoes_ALK_absoluta = models.BooleanField(unique=False, null=True)
	PP_Netshoes_ALK = models.FloatField(unique=False, null=True)

	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

	def __str__(self):
		return str(self.PP_sku)


class Fornecedores(models.Model):
	FN_ID = models.IntegerField(primary_key=True) # Codigo / até 15
	FN_Nome = models.CharField(max_length=200)
	def __str__(self):
		return self.FN_Nome


class Nota(models.Model):
	NT_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	NT_Num_NF = models.CharField(max_length=100,unique=False, null=True)
	NT_fornecedor = models.ForeignKey(Fornecedores, on_delete=models.CASCADE)
	NT_produtos = models.TextField()
	NT_User_create = models.CharField(max_length=100,unique=False, null=True)
	NT_visualizado = models.BooleanField(unique=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
	def __str__(self):
		return self.NT_Num_NF


class Kit(models.Model):
	KT_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	KT_principal = models.ForeignKey(Produto, on_delete=models.CASCADE)
	KT_variacoes = models.TextField()
	KT_principal_Sku = models.CharField(max_length=100,unique=False, null=True)
	def __str__(self):
		return str(self.KT_principal)


class Correcoes(models.Model):
	CR_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	CR_produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
	CR_sku = models.CharField(max_length=50,unique=False, null=True)
	CR_prioridade = models.CharField(max_length=100,unique=False, null=True)

	CR_status = models.CharField(max_length=100,unique=False, null=True)
	

	CR_motivo_correcao = models.TextField(unique=False, null=True)
	CR_links = models.TextField(unique=False, null=True)
	
	CR_portal_ML_alaok = models.BooleanField()
	CR_portal_ML_gea = models.BooleanField()
	CR_portal_ML_kes = models.BooleanField()
	CR_portal_ML_arrigo = models.BooleanField()

	CR_portal_Magalu_gea = models.BooleanField()
	CR_portal_Magalu_kes = models.BooleanField()
	CR_portal_Magalu_kc = models.BooleanField()
	CR_portal_Magalu_arrigo = models.BooleanField()

	CR_portal_b2w_alaok = models.BooleanField()
	CR_portal_b2w_kc = models.BooleanField()
	CR_portal_b2w_jcma = models.BooleanField()

	CR_portal_carrefour_alaok = models.BooleanField()
	CR_portal_carrefour_gea = models.BooleanField()
	CR_portal_carrefour_arrigo = models.BooleanField()

	CR_portal_netshoes_alk = models.BooleanField()
	CR_portal_netshoes_kes = models.BooleanField()

	CR_portal_centauro_alaok = models.BooleanField()

	CR_portal_olist_gea = models.BooleanField()
	CR_portal_olist_arrigo = models.BooleanField()

	CR_portal_leroy_kes = models.BooleanField()

	CR_portal_madeiramadeira_kes = models.BooleanField()
	CR_portal_madeiramadeira_arrigo = models.BooleanField()

	CR_portal_amazon_kes = models.BooleanField()
	CR_portal_amazon_kc = models.BooleanField()
	CR_portal_amazon_arrigo = models.BooleanField()

	CR_portal_cnova_kes = models.BooleanField()
	CR_portal_cnova_arrigo = models.BooleanField()

	CR_portal_shopee_kes = models.BooleanField()

	CR_portal_aliexpress_arrigo = models.BooleanField()

	CR_portal_mobly_kc = models.BooleanField()

	CR_portal_elo7_arrigo = models.BooleanField()
	CR_portal_Master = models.BooleanField(unique=False, null=True)

	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

	def __str__(self):
		return str(self.CR_sku)


class Correcoes_log(models.Model):
	CL_id = models.IntegerField(primary_key=True) # Codigo / até 15
	CL_produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
	CL_correcao = models.ForeignKey(Correcoes, on_delete=models.CASCADE)
	CL_campo = models.CharField(max_length=100,unique=False, null=True)
	CL_valor_antigo = models.CharField(max_length=100,unique=False, null=True)
	CL_valor_novo = models.CharField(max_length=100,unique=False, null=True)
	CL_user = models.CharField(max_length=100,unique=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)
	
	def __str__(self):
		return str(self.CL_produto)


class Produtos_Arrigo(models.Model):
	PA_ID = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	PA_sku = models.CharField(max_length=100,unique=False, null=True)
	PA_modelo = models.CharField(max_length=100,unique=False, null=True)
	PA_titulo = models.CharField(max_length=200,unique=False, null=True)
	PA_custo = models.CharField(max_length=200,unique=False, null=True)
	PA_preco_venda = models.CharField(max_length=200,unique=False, null=True)

	PA_imagem1 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem2 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem3 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem4 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem5 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem6 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem7 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem8 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem9 = models.CharField(max_length=250,unique=False, null=True)
	PA_imagem10 = models.CharField(max_length=250,unique=False, null=True)

	PA_cor = models.CharField(max_length=100,unique=False, null=True)	
	PA_verniz = models.CharField(max_length=100,unique=False, null=True)
	PA_tipo_tinta = models.CharField(max_length=100,unique=False, null=True)
	PA_escala_cor = models.CharField(max_length=100,unique=False, null=True)
	PA_material = models.CharField(max_length=100,unique=False, null=True)
	PA_material_especura = models.CharField(max_length=100,unique=False, null=True)
	PA_material_suporte = models.CharField(max_length=100,unique=False, null=True)
	PA_material_pintura_suporte = models.CharField(max_length=100,unique=False, null=True)
	PA_material_acabamento = models.CharField(max_length=100,unique=False, null=True)
	PA_localizacao = models.CharField(max_length=100,unique=False, null=True)
	PA_tipo_suporte = models.CharField(max_length=100,unique=False, null=True)
	PA_possui_pes = models.CharField(max_length=100,unique=False, null=True)
	PA_tipo_fixacao = models.CharField(max_length=100,unique=False, null=True)
	PA_envio = models.CharField(max_length=100,unique=False, null=True)

	PA_peso_suportado = models.FloatField()

	PA_capacidade_garrafas = models.IntegerField()
	PA_capacidade_copos = models.IntegerField()
	PA_capacidade_tacas = models.IntegerField()
	PA_quantidade_prateleiras = models.IntegerField()
	PA_quantidade_suportes = models.IntegerField()
	PA_quantidade_gavetas = models.IntegerField()
	
	PA_peso = models.FloatField()
	
	PA_medida_externa_altura = models.FloatField()
	PA_medida_externa_largura = models.FloatField()
	PA_medida_externa_profundidade = models.FloatField()

	PA_quantidade_parafusos_fixacao = models.IntegerField()
	
	PA_medidas_internas = models.TextField()

	created_at = models.DateTimeField(auto_now_add=True,unique=False, null=True)
	updated_at = models.DateTimeField(auto_now=True,unique=False, null=True)

	def __str__(self):
		return str(self.PA_sku)

class opcao_cor(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
		return str(self.valor)

class opcao_verniz(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_tipo_tinta(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_escala_cor(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_material(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)


class opcao_material_especura(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_material_suporte(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_material_pintura_suporte(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_material_acabamento(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_localizacao(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)
			
class opcao_tipo_suporte(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_possui_pes(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_tipo_fixacao(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

class opcao_envio(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	valor = models.CharField(max_length=100,unique=False, null=True)

	def __str__(self):
			return str(self.valor)

auditlog.register(Preco_Portal)
auditlog.register(Confere_Preco_log)
auditlog.register(Correcoes)
auditlog.register(Correcoes_log)