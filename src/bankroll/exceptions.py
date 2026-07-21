"""
AEGIS - Bankroll Domain Exceptions

Define as exceções específicas do domínio de gestão de banca.
"""


class BankrollError(Exception):
    """
    Exceção base do domínio de gestão de banca.
    """


class InvalidBankrollTransactionError(BankrollError):
    """
    Indica que uma transação financeira é inválida.
    """


class InvalidBankrollTransactionTypeError(
    InvalidBankrollTransactionError
):
    """
    Indica que o tipo da transação é inválido.
    """


class InvalidBankrollTransactionDirectionError(
    InvalidBankrollTransactionError
):
    """
    Indica que a direção contábil da transação é inválida.
    """


class InvalidBankrollTransactionAmountError(
    InvalidBankrollTransactionError
):
    """
    Indica que o valor da transação é inválido.
    """


class InvalidBankrollTransactionTimestampError(
    InvalidBankrollTransactionError
):
    """
    Indica que o horário da transação é inválido.
    """


class InvalidBankrollTransactionStatusError(
    InvalidBankrollTransactionError
):
    """
    Indica que o status da transação é inválido.
    """


class InvalidBankrollTransactionReferenceError(
    InvalidBankrollTransactionError
):
    """
    Indica que uma referência vinculada à transação é inválida.
    """


class IncompatibleBankrollTransactionDirectionError(
    InvalidBankrollTransactionError
):
    """
    Indica incompatibilidade entre o tipo da transação
    e sua direção contábil.
    """


class InsufficientBankrollBalanceError(BankrollError):
    """
    Indica que a banca não possui saldo disponível suficiente.
    """


class DuplicateBankrollTransactionError(BankrollError):
    """
    Indica tentativa de registrar uma transação já existente.
    """


class BankrollTransactionNotFoundError(BankrollError):
    """
    Indica que uma transação não foi encontrada no ledger.
    """


class BankrollTransactionAlreadyReversedError(BankrollError):
    """
    Indica que uma transação já foi estornada anteriormente.
    """


class InvalidBankrollBalanceError(BankrollError):
    """
    Indica que um saldo informado ou calculado é inválido.
    """