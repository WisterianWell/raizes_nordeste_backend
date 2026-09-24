from fastapi import status

from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException

def cliente_nao_encontrado() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.CLIENTE_NAO_ENCONTRADO,
        message="Cliente não encontrado.",
        details=[{
            "field": "id_cliente",
            "issue": "Cliente não encontrado"
        }]
    )

def funcionario_nao_encontrado() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.FUNCIONARIO_NAO_ENCONTRADO,
        message="Funcionário não encontrado.",
        details=[{
            "field": "id_funcionario",
            "issue": "Funcionário não encontrado"
        }]
    )

def unidade_nao_encontrada() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.UNIDADE_NAO_ENCONTRADA,
        message="Unidade não encontrada.",
        details=[{
            "field": "id_unidade",
            "issue": "Unidade não encontrada"
        }]
    )

def produto_nao_encontrado() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.PRODUTO_NAO_ENCONTRADO,
        message="Produto não encontrado.",
        details=[{
            "field": "id_produto",
            "issue": "Produto não encontrado"
        }]
    )

def item_cardapio_nao_encontrado() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.ITEM_CARDAPIO_NAO_ENCONTRADO,
        message="Produto não encontrado nessa unidade.",
        details=[{
            "field": "id_produto",
            "issue": "Produto não encontrado nessa unidade"
        }]
    )

def pedido_nao_encontrado() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.PEDIDO_NAO_ENCONTRADO,
        message="Pedido não encontrado.",
        details=[{
            "field": "id_pedido",
            "issue": "Pedido não encontrado"
        }]
    )

def promocao_nao_encontrada() -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCodes.PROMOCAO_NAO_ENCONTRADA,
        message="Promoção não encontrada.",
        details=[{
            "field": "id_promocao",
            "issue": "Promoção não encontrada"
        }]
    )

def acesso_negado_pedido() -> AppException:
    return AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        error_code=ErrorCodes.ACESSO_NEGADO,
        message="Você só pode acessar os seus próprios pedidos.",
        details=[{
            "field": "id_cliente",
            "issue": "Você só pode acessar os seus próprios pedidos"
        }]
    )

def cpf_ja_cadastrado() -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCodes.CPF_JA_CADASTRADO,
        message="CPF já cadastrado.",
        details=[{
            "field": "cpf",
            "issue": "CPF já cadastrado"
        }]
    )

def email_ja_cadastrado() -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCodes.EMAIL_JA_CADASTRADO,
        message="Email já cadastrado.",
        details=[{
            "field": "email",
            "issue": "Email já cadastrado"
        }]
    )

def unidade_nao_permitida() -> AppException:
    return AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        error_code=ErrorCodes.UNIDADE_NAO_PERMITIDA,
        message="Você só pode acessar recursos da sua própria unidade.",
        details=[{
            "field": "id_unidade",
            "issue": "Funcionário só tem acesso à unidade associada ao seu cadastro"
        }]
    )

def unidade_fechada() -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCodes.UNIDADE_FECHADA,
        message="Unidade está fechada no momento.",
        details=[{
            "field": "id_unidade",
            "issue": "Unidade está fechada e não pode receber novos pedidos"
        }]
    )

def restrito_cargo_admin() -> AppException:
    return AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        error_code=ErrorCodes.RESTRITO_CARGO_ADMIN,
        message="Apenas administradores podem atribuir o cargo ADMIN a um funcionário.",
        details=[{
            "field": "cargo",
            "issue": "Somente um funcionário ADMIN pode definir o cargo ADMIN"
        }]
    )
