"""
AEGIS - Bankroll Transaction Entity.

Define a entidade imutável que representa uma movimentação financeira
registrada no ledger do domínio Bankroll.

A entidade garante apenas a integridade estrutural dos dados. As regras
que determinam o tipo e a direção corretos de cada operação pertencem à
BankrollTransactionFactory.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    InvalidBankrollTransactionAmountError,
    InvalidBankrollTransactionDirectionError,
    InvalidBankrollTransactionReferenceError,
    InvalidBankrollTransactionStatusError,
    InvalidBankrollTransactionTimestampError,
    InvalidBankrollTransactionTypeError,
)


@dataclass(frozen=True, slots=True)
class BankrollTransaction:
    """
    Representa uma movimentação financeira imutável da banca.

    A transação registra um fato ocorrido no ledger. Depois de criada,
    não pode ser alterada.

    Attributes:
        transaction_type:
            Tipo da movimentação financeira.

        direction:
            Direção contábil da movimentação.

        amount:
            Valor absoluto da movimentação.

        created_at:
            Data e hora da criação, obrigatoriamente com timezone.

        contract_id:
            Identificador opcional do contrato associado.

        description:
            Descrição opcional para leitura humana.

        reference:
            Referência externa opcional.

        transaction_id:
            Identificador único da transação.

        status:
            Estado de processamento da entrada no ledger.
    """

    transaction_type: BankrollTransactionType
    direction: BankrollTransactionDirection
    amount: Decimal
    created_at: datetime
    contract_id: UUID | None = None
    description: str | None = None
    reference: str | None = None
    transaction_id: UUID = field(default_factory=uuid4)
    status: BankrollEntryStatus = BankrollEntryStatus.REGISTERED

    def __post_init__(self) -> None:
        """Valida e normaliza os dados da entidade."""

        self._validate_transaction_type()
        self._validate_direction()
        self._validate_amount()
        self._validate_created_at()
        self._validate_contract_id()
        self._validate_transaction_id()
        self._validate_status()

        normalized_description = self._normalize_optional_text(
            value=self.description,
            field_name="description",
        )
        normalized_reference = self._normalize_optional_text(
            value=self.reference,
            field_name="reference",
        )

        object.__setattr__(
            self,
            "description",
            normalized_description,
        )
        object.__setattr__(
            self,
            "reference",
            normalized_reference,
        )

    @property
    def signed_amount(self) -> Decimal:
        """
        Retorna o valor com o sinal correspondente à direção financeira.

        Returns:
            Valor positivo para crédito, negativo para débito e zero para
            movimentações neutras.
        """

        if self.direction is BankrollTransactionDirection.CREDIT:
            return self.amount

        if self.direction is BankrollTransactionDirection.DEBIT:
            return -self.amount

        return Decimal("0")

    @property
    def affects_balance(self) -> bool:
        """
        Informa se a movimentação altera diretamente o saldo.

        Returns:
            True para créditos e débitos; False para entradas neutras.
        """

        return self.direction in {
            BankrollTransactionDirection.CREDIT,
            BankrollTransactionDirection.DEBIT,
        }

    def _validate_transaction_type(self) -> None:
        """Valida o tipo da transação."""

        if not isinstance(
            self.transaction_type,
            BankrollTransactionType,
        ):
            raise InvalidBankrollTransactionTypeError(
                "transaction_type deve ser uma instância de "
                "BankrollTransactionType"
            )

    def _validate_direction(self) -> None:
        """Valida a direção contábil da transação."""

        if not isinstance(
            self.direction,
            BankrollTransactionDirection,
        ):
            raise InvalidBankrollTransactionDirectionError(
                "direction deve ser uma instância de "
                "BankrollTransactionDirection"
            )

    def _validate_amount(self) -> None:
        """
        Valida o valor da movimentação.

        Regras:
            - deve ser Decimal;
            - deve ser finito;
            - não pode ser negativo;
            - créditos e débitos devem ser maiores que zero;
            - entradas neutras devem possuir valor zero.
        """

        if not isinstance(self.amount, Decimal):
            raise InvalidBankrollTransactionAmountError(
                "amount deve ser uma instância de Decimal"
            )

        if not self.amount.is_finite():
            raise InvalidBankrollTransactionAmountError(
                "amount deve ser um valor finito"
            )

        if self.amount < Decimal("0"):
            raise InvalidBankrollTransactionAmountError(
                "amount não pode ser negativo"
            )

        if (
            self.direction
            in {
                BankrollTransactionDirection.CREDIT,
                BankrollTransactionDirection.DEBIT,
            }
            and self.amount == Decimal("0")
        ):
            raise InvalidBankrollTransactionAmountError(
                "transações CREDIT ou DEBIT devem possuir "
                "amount maior que zero"
            )

        if (
            self.direction is BankrollTransactionDirection.NEUTRAL
            and self.amount != Decimal("0")
        ):
            raise InvalidBankrollTransactionAmountError(
                "transações NEUTRAL devem possuir amount igual a zero"
            )

    def _validate_created_at(self) -> None:
        """Valida a data e hora da transação."""

        if not isinstance(self.created_at, datetime):
            raise InvalidBankrollTransactionTimestampError(
                "created_at deve ser uma instância de datetime"
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise InvalidBankrollTransactionTimestampError(
                "created_at deve possuir timezone"
            )

    def _validate_contract_id(self) -> None:
        """Valida o identificador opcional do contrato."""

        if (
            self.contract_id is not None
            and not isinstance(self.contract_id, UUID)
        ):
            raise InvalidBankrollTransactionReferenceError(
                "contract_id deve ser UUID ou None"
            )

    def _validate_transaction_id(self) -> None:
        """Valida o identificador único da transação."""

        if not isinstance(self.transaction_id, UUID):
            raise InvalidBankrollTransactionReferenceError(
                "transaction_id deve ser uma instância de UUID"
            )

    def _validate_status(self) -> None:
        """Valida o estado da entrada no ledger."""

        if not isinstance(self.status, BankrollEntryStatus):
            raise InvalidBankrollTransactionStatusError(
                "status deve ser uma instância de BankrollEntryStatus"
            )

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
        field_name: str,
    ) -> str | None:
        """
        Valida e normaliza um campo textual opcional.

        Args:
            value:
                Valor que será validado.

            field_name:
                Nome do campo utilizado na mensagem de erro.

        Returns:
            Texto sem espaços nas extremidades ou None.

        Raises:
            InvalidBankrollTransactionReferenceError:
                Quando o valor não for str nem None.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            raise InvalidBankrollTransactionReferenceError(
                f"{field_name} deve ser str ou None"
            )

        normalized_value = value.strip()

        if not normalized_value:
            return None

        return normalized_value