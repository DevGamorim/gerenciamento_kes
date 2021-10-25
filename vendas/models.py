from django.db import models
from auditlog.registry import auditlog
from django.conf import settings
import jsonfield

# Create your models here.
class Venda(models.Model):
	VE_Codigo = models.IntegerField(primary_key=True) #int
	VE_NaoPersistir = models.BooleanField() #boolean
	VE_ClienteCodigo = models.IntegerField() #int
	VE_ClienteTipoPessoa = models.TextField() #str
	VE_ClienteDocumento = models.TextField() #str
	VE_ClienteIdentidade = models.TextField() #str
	VE_TransportadoraCodigo = models.IntegerField() #int
	VE_ValorTotal = models.FloatField() #float
	VE_ValorFrete = models.FloatField() #float
	VE_ValorEncargos = models.FloatField() #float
	VE_ValorDesconto = models.FloatField() #float
	VE_ValorComissao = models.FloatField() #float
	VE_DataVenda = models.DateTimeField() #date
	VE_DataPagamento = models.DateTimeField() #date
	VE_Entrega = models.BooleanField() #boolean
	VE_EntregaNome = models.TextField() #str
	VE_EntregaEmail = models.TextField() #str
	VE_NumeroObjeto = models.TextField() #str
	VE_EntregaTelefone = models.TextField() #str
	VE_EntregaLogradouro = models.TextField() #str
	VE_EntregaLogradouroNumero = models.TextField() #str
	VE_EntregaLogradouroComplemento = models.TextField() #str
	VE_EntregaBairro = models.TextField() #str
	VE_EntregaMunicipioNome = models.TextField() #str
	VE_EntregaUnidadeFederativa = models.TextField() #str
	VE_EntregaCEP = models.TextField() #str
	VE_CupomDescontoCodigo = models.TextField() #str
	VE_CupomDescontoValor = models.FloatField() #float
	VE_Observacoes = models.TextField() #str
	VE_ObservacoesLoja = models.TextField() #str
	VE_CodigoStatus = models.IntegerField() #int
	VE_DescricaoStatus = models.TextField() #str
	VE_DataHoraStatus = models.DateTimeField() #date
	VE_StatusID = models.IntegerField() #int
	VE_NotificarCliente = models.BooleanField() #boolean
	VE_PrevisaoEntrega = models.DateTimeField() #date
	VE_OrigemPedido = models.TextField() #str
	VE_OrigemExterno = models.TextField() #str
	VE_CodigoPedidoExterno = models.TextField() #str
	VE_CodigoPedido = models.IntegerField() #int
	VE_CodigoNotaFiscal = models.IntegerField() #int
	VE_DataEntrega = models.DateTimeField() #date
	VE_Empresa = models.TextField() #str
	VE_OrcamentoImpresso = models.BooleanField() #boolean
	VE_ValorTotalBruto = models.FloatField() #float
	VE_Orcamento = models.BooleanField() #boolean
	VE_TipoVenda = models.TextField() #str
	VE_ClienteNome = models.TextField() #str
	VE_HoraVenda = models.DateTimeField() #date
	VE_Origem = models.TextField() #str
	VE_Cancelada = models.BooleanField() #boolean
	VE_EnviarEmail = models.BooleanField() #boolean
	VE_Reservada = models.BooleanField() #boolean
	VE_VendaPagamentos = jsonfield.JSONField() #str infinito
	VE_Itens = jsonfield.JSONField() #str infinito
	VE_PesoLiquido = models.FloatField() #float
	VE_Status = jsonfield.JSONField() #str infinito
	VE_ClienteTipoDesconto = models.TextField() #str
	VE_ClienteDesconto = models.FloatField() #float
	VE_FormaParcelamentoCodigo = models.IntegerField() #int
	VE_TransportadoraNome = models.TextField() #str
	VE_Parcelas = jsonfield.JSONField() #str infinito
	VE_DataCancelamento = models.DateTimeField() #date
	VE_ClienteCodigoAnterior = models.IntegerField() #int
	VE_DataEnvio = models.DateTimeField() #date
	VE_HoraEnvio = models.DateTimeField() #date
	VE_PacoteID = models.TextField() #str
	VE_Pacotes = jsonfield.JSONField() #str infinito
	VE_NotaFiscalNumero = models.IntegerField() #int
	VE_Danfe = models.TextField() #str
	VE_PrevisaoEntregaEmDias = models.IntegerField() #int
	VE_Conferido = models.BooleanField() #boolean
	VE_UsuarioConferencia = models.IntegerField() #int
	VE_NumeroObjetoGeradoPeloSite = models.BooleanField() #boolean
	VE_NFImpressa = models.BooleanField() #boolean
	VE_PrevisaoEnvio = models.DateTimeField() #date
	VE_TransportadoraCodigoAnterior = models.IntegerField() #int
	VE_FreteSimulado = models.FloatField() #float
	VE_TipoDeCalculoDeFrete = models.TextField() #str
	VE_DataColeta = models.DateTimeField() #date
	VE_TransportadoraMuirCodigo = models.IntegerField() #int
	VE_EmbalagemId = models.IntegerField() #int
	VE_NotaCupom = models.TextField() #str
	VE_ECFSerie = models.TextField() #str
	VE_ECFNumero = models.IntegerField() #int
	VE_Volumes = models.IntegerField() #int
	VE_CodigoIntermediador = models.IntegerField() #int
	VE_CNPJIntermediador = models.TextField() #str
	VE_CNPJIntermediadorPagamento = models.TextField() #str
	VE_IdentificadorIntermediador = models.TextField() #str
	VE_MuirIntegracao = models.IntegerField() #int
	VE_ChaveUnica = models.TextField() #str
	VE_EntregaMunicipio = models.TextField() #str
	VE_FormasDePagamento = models.TextField() #str

	def __str__(self):
		return str(self.VE_Codigo)