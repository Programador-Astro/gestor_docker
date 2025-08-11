from .users import Usuario, Perfil  # Ajuste o nome da classe se for diferente
from .clientes import Clientes, Pedido, Produto, PedidoProduto  # Ajuste se necessário
from .veiculos import Veiculos, Checklist  # Ajuste se necessário


# Exporta todos os modelos para facilitar importações
__all__ = [
    "Usuario",
    "Perfil",
    "Clientes",
    "Pedido",
    "Produto",
    "PedidoProduto",
    "Veiculos",
    "Checklist"
]
