"""
AEGIS - Bankroll Domain

Expõe os principais componentes públicos do domínio
de gestão financeira da banca.
"""

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    BankrollError,
    BankrollTransactionAlreadyReversedError,
    BankrollTransactionNotFoundError,
    DuplicateBankrollTransactionError,
    IncompatibleBankrollTransactionDirectionError,
    InsufficientBankrollBalanceError,
    InvalidBankrollBalanceError,
    InvalidBankrollTransactionAmountError,
    InvalidBankrollTransactionDirectionError,
    InvalidBankrollTransactionError,
    InvalidBankrollTransactionReferenceError,
    InvalidBankrollTransactionStatusError,
    InvalidBankrollTransactionTimestampError,
    InvalidBankrollTransactionTypeError,
)
from src.bankroll.transaction import BankrollTransaction

__all__ = [
    "BankrollEntryStatus",
    "BankrollError",
    "BankrollTransaction",
    "BankrollTransactionAlreadyReversedError",
    "BankrollTransactionDirection",
    "BankrollTransactionNotFoundError",
    "BankrollTransactionType",
    "DuplicateBankrollTransactionError",
    "IncompatibleBankrollTransactionDirectionError",
    "InsufficientBankrollBalanceError",
    "InvalidBankrollBalanceError",
    "InvalidBankrollTransactionAmountError",
    "InvalidBankrollTransactionDirectionError",
    "InvalidBankrollTransactionError",
    "InvalidBankrollTransactionReferenceError",
    "InvalidBankrollTransactionStatusError",
    "InvalidBankrollTransactionTimestampError",
    "InvalidBankrollTransactionTypeError",
]