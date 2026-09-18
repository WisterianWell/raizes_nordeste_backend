from enum import Enum

class TipoUsuario(str, Enum):
    CLIENTE = "CLIENTE"
    FUNCIONARIO = "FUNCIONARIO"

class CargoFunc(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"

class CanalPedido(str, Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"

class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class FormaPagamento(str, Enum):
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    PIX = "PIX"
    DINHEIRO = "DINHEIRO"

class StatusPagamento(str, Enum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
    ESTORNADO = "ESTORNADO"

class TipoMovimentacao(str, Enum):
    VENDA = "VENDA"
    CANCELAMENTO = "CANCELAMENTO"
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
