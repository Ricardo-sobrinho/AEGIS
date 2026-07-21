"""
AEGIS - Bankroll Domain Enumerations

Define os tipos padronizados utilizados pelo domínio de gestão
financeira das operações de contratos de tempo fixo.
"""

from enum import StrEnum


class BankrollTransactionType(StrEnum):
    """
    Tipos de movimentação financeira registradas na banca.

    Cada movimentação representa um evento imutável no ledger
    financeiro do BankrollEngine.
    """

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

    STAKE_RESERVED = "STAKE_RESERVED"
    STAKE_RELEASED = "STAKE_RELEASED"

    SETTLEMENT_WIN = "SETTLEMENT_WIN"
    SETTLEMENT_LOSS = "SETTLEMENT_LOSS"
    SETTLEMENT_DRAW = "SETTLEMENT_DRAW"

    CREDIT_ADJUSTMENT = "CREDIT_ADJUSTMENT"
    DEBIT_ADJUSTMENT = "DEBIT_ADJUSTMENT"


class BankrollTransactionDirection(StrEnum):
    """
    Direção contábil da movimentação financeira.

    CREDIT:
        Aumenta o saldo financeiro da banca.

    DEBIT:
        Reduz o saldo financeiro da banca.

    NEUTRAL:
        Registra um evento financeiro sem alterar diretamente o saldo.
    """

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    NEUTRAL = "NEUTRAL"


class BankrollEntryStatus(StrEnum):
    """
    Estado de processamento de uma entrada no ledger.

    REGISTERED:
        A transação foi registrada com sucesso.

    REVERSED:
        A transação foi compensada por uma transação de estorno.

    RECONCILING:
        A movimentação está aguardando conciliação.

    UNKNOWN:
        O estado financeiro não pôde ser confirmado.
    """

    REGISTERED = "REGISTERED"
    REVERSED = "REVERSED"
    RECONCILING = "RECONCILING"
    UNKNOWN = "UNKNOWN"