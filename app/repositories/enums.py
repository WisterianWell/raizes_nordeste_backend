from enum import Enum

class TipoUsuario(str, Enum):
    CLIENTE = "CLIENTE"
    FUNCIONARIO = "FUNCIONARIO"

class CargoFunc(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
