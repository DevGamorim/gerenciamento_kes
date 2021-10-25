from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.producao, name='irpedidos'),
    path('NovoPedido/', views.Novo_pedido, name='irnovopedido'),
    path('Historico/', views.historico, name='irhistoricopedidos'),
    path('Produção/', views.producao, name='irproducao'),
    path('Pedidos/', views.pedidos, name='irpedido'),
    path('Editar/', views.editar, name='ireditarpedidos'),
    path('Relatorio/', views.relatorio, name='irrelatoriopedidos'),
    path('Estoque/', views.estoque, name='irestoquepedi'),
    path('EditarEstoque/', views.estoqueedit, name='irestoqueedit'),
    path('BaixaEstoque/', views.estoquebaixa, name='irestoquebaixa'),
    path('AdicionaEstoque/', views.estoqueadiciona, name='irestoqueadiciona'),
    path('EditarSKU/', views.conexaoeditar, name='ireditarsku'),
    
]
