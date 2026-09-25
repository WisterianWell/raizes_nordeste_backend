from datetime import datetime

from app.domain.enums import CanalPedido, StatusPedido, TipoDesconto

# promoção
def periodo_valido(data_inicio: datetime, data_fim: datetime) -> bool:
    return data_fim > data_inicio

def desconto_percentual_valido(valor_desc: float) -> bool:
    return 0 < valor_desc <= 100

def calcular_preco_com_desconto(preco: float, itens_vigentes) -> float:
    preco_desc = preco
    for item in itens_vigentes:
        if item.tipo_desc == TipoDesconto.PERCENTUAL.value:
            preco_com_desconto = preco * (1 - float(item.valor_desc) / 100)
        else:
            preco_com_desconto = preco - float(item.valor_desc)
        preco_desc = min(preco_desc, max(0.0, preco_com_desconto))
    return preco_desc

# pedido
STATUS_FINALIZADOS = {StatusPedido.ENTREGUE.value, StatusPedido.CANCELADO.value}
CANAIS_CLIENTE_OBRIGATORIO = {CanalPedido.APP.value, CanalPedido.WEB.value, CanalPedido.PICKUP.value}
ORDEM_STATUS = [
    StatusPedido.PENDENTE.value,
    StatusPedido.EM_PREPARO.value,
    StatusPedido.PRONTO.value,
    StatusPedido.ENTREGUE.value,
]

def esta_finalizado(status_pedido: str) -> bool:
    return status_pedido in STATUS_FINALIZADOS

def proximo_status(status_pedido: str) -> str:
    indice_atual = ORDEM_STATUS.index(status_pedido)
    return ORDEM_STATUS[indice_atual + 1]

def cliente_obrigatorio_para_canal(canal: str) -> bool:
    return canal in CANAIS_CLIENTE_OBRIGATORIO

# fidelização
PONTOS_POR_REAL = 1
DESC_POR_PONTO = 0.1

def calcular_pontos_ganhos(valor: float) -> int:
    return int(valor * PONTOS_POR_REAL)

def calcular_desconto_pontos(pontos: int) -> float:
    return pontos * DESC_POR_PONTO
