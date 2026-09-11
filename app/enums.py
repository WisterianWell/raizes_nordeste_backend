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
