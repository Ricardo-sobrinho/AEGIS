"""
AEGIS - Bankroll Transaction Tests.

Testes unitários da entidade imutável BankrollTransaction.

A entidade é responsável por validar somente a integridade estrutural de
uma transação financeira, incluindo:

- tipo da transação;
- direção financeira;
- valor monetário;
- timestamp com timezone;
- identificadores UUID;
- status da entrada;
- textos opcionais;
- cálculo do valor assinado;
- indicação de impacto no saldo.

A compatibilidade entre transaction_type e direction não pertence à
entidade. Essa regra é responsabilidade da BankrollTransactionFactory.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
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
from src.bankroll.transaction import BankrollTransaction


class TestBankrollTransaction(unittest.TestCase):
    """Testes unitários da entidade BankrollTransaction."""

    def setUp(self) -> None:
        """Prepara valores válidos reutilizados nos testes."""

        self.transaction_id = uuid4()
        self.contract_id = uuid4()
        self.amount = Decimal("100.00")
        self.created_at = datetime(
            year=2026,
            month=7,
            day=20,
            hour=12,
            minute=30,
            second=45,
            tzinfo=UTC,
        )

    def create_valid_transaction(
        self,
        *,
        transaction_type: BankrollTransactionType = (
            BankrollTransactionType.DEPOSIT
        ),
        direction: BankrollTransactionDirection = (
            BankrollTransactionDirection.CREDIT
        ),
        amount: Decimal = Decimal("100.00"),
        transaction_id: UUID | None = None,
        contract_id: UUID | None = None,
        status: BankrollEntryStatus = (
            BankrollEntryStatus.REGISTERED
        ),
        description: str | None = None,
        reference: str | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação válida para reduzir repetição nos testes.

        Args:
            transaction_type:
                Tipo da transação financeira.
            direction:
                Direção financeira da transação.
            amount:
                Valor absoluto da transação.
            transaction_id:
                Identificador opcional da transação.
            contract_id:
                Identificador opcional do contrato.
            status:
                Status contábil da entrada.
            description:
                Descrição opcional.
            reference:
                Referência externa opcional.
            created_at:
                Timestamp opcional da criação.

        Returns:
            Uma BankrollTransaction válida.
        """

        return BankrollTransaction(
            transaction_type=transaction_type,
            direction=direction,
            amount=amount,
            transaction_id=transaction_id or uuid4(),
            contract_id=contract_id,
            status=status,
            description=description,
            reference=reference,
            created_at=created_at or self.created_at,
        )

    def test_should_create_valid_transaction(self) -> None:
        """Deve criar uma transação válida com todos os campos."""

        transaction = BankrollTransaction(
            transaction_type=BankrollTransactionType.STAKE_RESERVED,
            direction=BankrollTransactionDirection.DEBIT,
            amount=self.amount,
            transaction_id=self.transaction_id,
            contract_id=self.contract_id,
            status=BankrollEntryStatus.REGISTERED,
            description="Reserva da entrada",
            reference="ORDER-001",
            created_at=self.created_at,
        )

        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.STAKE_RESERVED,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.DEBIT,
        )
        self.assertEqual(transaction.amount, self.amount)
        self.assertEqual(
            transaction.transaction_id,
            self.transaction_id,
        )
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )
        self.assertEqual(
            transaction.description,
            "Reserva da entrada",
        )
        self.assertEqual(transaction.reference, "ORDER-001")
        self.assertEqual(transaction.created_at, self.created_at)

    def test_should_generate_unique_transaction_ids(self) -> None:
        """Deve gerar IDs diferentes quando transaction_id for omitido."""

        first_transaction = BankrollTransaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=self.amount,
            created_at=self.created_at,
        )
        second_transaction = BankrollTransaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertIsInstance(
            first_transaction.transaction_id,
            UUID,
        )
        self.assertIsInstance(
            second_transaction.transaction_id,
            UUID,
        )
        self.assertNotEqual(
            first_transaction.transaction_id,
            second_transaction.transaction_id,
        )

    def test_should_accept_explicit_transaction_id(self) -> None:
        """Deve preservar o transaction_id informado."""

        transaction = self.create_valid_transaction(
            transaction_id=self.transaction_id,
        )

        self.assertEqual(
            transaction.transaction_id,
            self.transaction_id,
        )

    def test_should_use_registered_as_default_status(self) -> None:
        """Deve utilizar REGISTERED como status padrão."""

        transaction = BankrollTransaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_be_immutable(self) -> None:
        """Deve impedir a alteração dos campos após a criação."""

        transaction = self.create_valid_transaction()

        with self.assertRaises(FrozenInstanceError):
            transaction.amount = Decimal("200.00")  # type: ignore[misc]

    def test_should_use_slots(self) -> None:
        """Deve utilizar slots e não possuir __dict__ de instância."""

        transaction = self.create_valid_transaction()

        self.assertFalse(hasattr(transaction, "__dict__"))

    def test_should_normalize_description_and_reference(self) -> None:
        """Deve remover espaços externos dos textos opcionais."""

        transaction = self.create_valid_transaction(
            description="  Aporte inicial  ",
            reference="  BANK-001  ",
        )

        self.assertEqual(
            transaction.description,
            "Aporte inicial",
        )
        self.assertEqual(transaction.reference, "BANK-001")

    def test_should_convert_empty_optional_text_to_none(self) -> None:
        """Deve converter textos vazios ou em branco para None."""

        transaction = self.create_valid_transaction(
            description="   ",
            reference="",
        )

        self.assertIsNone(transaction.description)
        self.assertIsNone(transaction.reference)

    def test_credit_should_have_positive_signed_amount(self) -> None:
        """Crédito deve produzir signed_amount positivo."""

        transaction = self.create_valid_transaction(
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("150.50"),
        )

        self.assertEqual(
            transaction.signed_amount,
            Decimal("150.50"),
        )

    def test_debit_should_have_negative_signed_amount(self) -> None:
        """Débito deve produzir signed_amount negativo."""

        transaction = self.create_valid_transaction(
            transaction_type=BankrollTransactionType.WITHDRAWAL,
            direction=BankrollTransactionDirection.DEBIT,
            amount=Decimal("150.50"),
        )

        self.assertEqual(
            transaction.signed_amount,
            Decimal("-150.50"),
        )

    def test_neutral_should_have_zero_signed_amount(self) -> None:
        """Direção neutra deve produzir signed_amount igual a zero."""

        transaction = self.create_valid_transaction(
            transaction_type=(
                BankrollTransactionType.SETTLEMENT_LOSS
            ),
            direction=BankrollTransactionDirection.NEUTRAL,
            amount=Decimal("0"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            transaction.signed_amount,
            Decimal("0"),
        )

    def test_credit_should_affect_balance(self) -> None:
        """Transação de crédito deve afetar o saldo."""

        transaction = self.create_valid_transaction(
            direction=BankrollTransactionDirection.CREDIT,
        )

        self.assertTrue(transaction.affects_balance)

    def test_debit_should_affect_balance(self) -> None:
        """Transação de débito deve afetar o saldo."""

        transaction = self.create_valid_transaction(
            transaction_type=BankrollTransactionType.WITHDRAWAL,
            direction=BankrollTransactionDirection.DEBIT,
        )

        self.assertTrue(transaction.affects_balance)

    def test_neutral_should_not_affect_balance(self) -> None:
        """Transação neutra não deve afetar diretamente o saldo."""

        transaction = self.create_valid_transaction(
            transaction_type=(
                BankrollTransactionType.SETTLEMENT_LOSS
            ),
            direction=BankrollTransactionDirection.NEUTRAL,
            amount=Decimal("0"),
            contract_id=self.contract_id,
        )

        self.assertFalse(transaction.affects_balance)

    def test_should_reject_invalid_transaction_type(self) -> None:
        """Deve rejeitar transaction_type fora do enum do domínio."""

        with self.assertRaises(
            InvalidBankrollTransactionTypeError
        ):
            BankrollTransaction(
                transaction_type="DEPOSIT",  # type: ignore[arg-type]
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                created_at=self.created_at,
            )

    def test_should_reject_invalid_direction(self) -> None:
        """Deve rejeitar direction fora do enum do domínio."""

        with self.assertRaises(
            InvalidBankrollTransactionDirectionError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction="CREDIT",  # type: ignore[arg-type]
                amount=self.amount,
                created_at=self.created_at,
            )

    def test_should_reject_non_decimal_amount(self) -> None:
        """Deve rejeitar amount que não seja Decimal."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=100.00,  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_negative_amount(self) -> None:
        """Deve rejeitar valores monetários negativos."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                amount=Decimal("-0.01"),
            )

    def test_should_reject_nan_amount(self) -> None:
        """Deve rejeitar valores Decimal NaN."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                amount=Decimal("NaN"),
            )

    def test_should_reject_infinite_amount(self) -> None:
        """Deve rejeitar infinito positivo."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                amount=Decimal("Infinity"),
            )

    def test_should_reject_negative_infinite_amount(self) -> None:
        """Deve rejeitar infinito negativo."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                amount=Decimal("-Infinity"),
            )

    def test_should_reject_zero_credit_amount(self) -> None:
        """Deve rejeitar crédito com valor igual a zero."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("0"),
            )

    def test_should_reject_zero_debit_amount(self) -> None:
        """Deve rejeitar débito com valor igual a zero."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("0"),
            )

    def test_should_reject_non_zero_neutral_amount(self) -> None:
        """Deve rejeitar direção neutra com valor diferente de zero."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            self.create_valid_transaction(
                transaction_type=(
                    BankrollTransactionType.SETTLEMENT_LOSS
                ),
                direction=BankrollTransactionDirection.NEUTRAL,
                amount=Decimal("10.00"),
                contract_id=self.contract_id,
            )

    def test_should_reject_non_datetime_timestamp(self) -> None:
        """Deve rejeitar created_at que não seja datetime."""

        with self.assertRaises(
            InvalidBankrollTransactionTimestampError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                created_at="2026-07-20",  # type: ignore[arg-type]
            )

    def test_should_reject_naive_datetime(self) -> None:
        """Deve rejeitar datetime sem timezone."""

        naive_datetime = datetime(
            year=2026,
            month=7,
            day=20,
            hour=12,
        )

        with self.assertRaises(
            InvalidBankrollTransactionTimestampError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                created_at=naive_datetime,
            )

    def test_should_reject_invalid_transaction_id(self) -> None:
        """Deve rejeitar transaction_id que não seja UUID."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                transaction_id="invalid-id",  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_contract_id(self) -> None:
        """Deve rejeitar contract_id que não seja UUID nem None."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            self.create_valid_transaction(
                contract_id="invalid-id",  # type: ignore[arg-type]
            )

    def test_should_accept_none_contract_id(self) -> None:
        """Deve aceitar contract_id igual a None."""

        transaction = self.create_valid_transaction(
            contract_id=None,
        )

        self.assertIsNone(transaction.contract_id)

    def test_should_accept_valid_contract_id(self) -> None:
        """Deve preservar um contract_id UUID válido."""

        transaction = self.create_valid_transaction(
            contract_id=self.contract_id,
        )

        self.assertEqual(
            transaction.contract_id,
            self.contract_id,
        )

    def test_should_reject_invalid_status(self) -> None:
        """Deve rejeitar status fora do enum BankrollEntryStatus."""

        with self.assertRaises(
            InvalidBankrollTransactionStatusError
        ):
            BankrollTransaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                status="REGISTERED",  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_accept_all_valid_statuses(self) -> None:
        """Deve aceitar todos os status definidos pelo domínio."""

        for status in BankrollEntryStatus:
            with self.subTest(status=status):
                transaction = self.create_valid_transaction(
                    status=status,
                )

                self.assertIs(transaction.status, status)

    def test_should_reject_invalid_description_type(self) -> None:
        """Deve rejeitar description que não seja str nem None."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            self.create_valid_transaction(
                description=123,  # type: ignore[arg-type]
            )

    def test_should_reject_invalid_reference_type(self) -> None:
        """Deve rejeitar reference que não seja str nem None."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            self.create_valid_transaction(
                reference=[],  # type: ignore[arg-type]
            )

    def test_entity_should_not_validate_type_direction_compatibility(
        self,
    ) -> None:
        """
        A entidade não deve validar compatibilidade entre tipo e direção.

        Essa responsabilidade pertence à BankrollTransactionFactory.
        """

        transaction = self.create_valid_transaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.DEBIT,
            amount=Decimal("100.00"),
        )

        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.DEPOSIT,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.DEBIT,
        )
        self.assertEqual(
            transaction.signed_amount,
            Decimal("-100.00"),
        )


if __name__ == "__main__":
    unittest.main()