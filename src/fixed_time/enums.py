"""
AEGIS - Fixed Time Trading Enums

Define todos os tipos enumerados utilizados pelo domínio de
contratos de tempo fixo.
"""

from enum import StrEnum


class FixedTimeDirection(StrEnum):
    """
    Direção de um contrato de tempo fixo.
    """

    CALL = "CALL"
    PUT = "PUT"


class ContractResult(StrEnum):
    """
    Resultado final de um contrato.
    """

    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"


class OperationalMode(StrEnum):
    """
    Modo operacional da AEGIS.
    """

    PAPER = "PAPER"
    DEMO = "DEMO"
    REAL = "REAL"


class ContractStatus(StrEnum):
    """
    Estados possíveis durante o ciclo de vida de um contrato.
    """

    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    OPEN = "OPEN"
    EXPIRED = "EXPIRED"
    SETTLED = "SETTLED"

    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"