import uuid
from datetime import datetime, timezone

from app.enums import StatusPagamento

class GatewayPagamentoMock:

    def processar_pagamento(
        self, id_pedido: int, valor: float, forma_pagamento: str, force_status: str | None = None
    ) -> dict:
        solicitacao = {
            "id_pedido": id_pedido,
            "valor": valor,
            "forma_pagamento": forma_pagamento,
        }

        aprovado = force_status != StatusPagamento.RECUSADO.value

        return {
            "status": StatusPagamento.APROVADO.value if aprovado else StatusPagamento.RECUSADO.value,
            "id_transacao": f"{uuid.uuid4()}",
            "codigo_autorizacao": f"{uuid.uuid4()}" if aprovado else None,
            "valor_processado": solicitacao["valor"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
