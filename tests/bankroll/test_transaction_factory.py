"""
AEGIS - Bankroll Transaction Factory Tests.

Valida o contrato público da BankrollTransactionFactory e garante que
cada operação financeira produza uma BankrollTransaction coerente com
as regras definidas pelo domínio Bankroll.

A factory é responsável por:

- selecionar o tipo correto da transação;
- selecionar a direção contábil correta;
- exigir contract_id nas operações vinculadas a contratos;
- gerar UUID quando transaction_id não for informado;
- gerar timestamp UTC quando created_at não for informado;
- registrar novas entradas com status REGISTERED;
- delegar à entidade as validações estruturais dos dados;
- impedir combinações incompatíveis entre tipo e direção.

A factory não atualiza saldos e não verifica disponibilidade financeira.
Essas responsabilidades pertencem ao BankrollEngine.
"""

import unittest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    IncompatibleBankrollTransactionDirectionError,
    InvalidBankrollTransactionAmountError,
    InvalidBankrollTransactionReferenceError,
    InvalidBankrollTransactionTimestampError,
)
from src.bankroll.transaction import BankrollTransaction
from src.bankroll.transaction_factory import BankrollTransactionFactory


class TestBankrollTransactionFactory(unittest.TestCase):
    """Testes unitários da BankrollTransactionFactory."""

    def setUp(self) -> None:
        """Prepara valores válidos reutilizados pelos testes."""

        self.amount = Decimal("100.00")
        self.contract_id = uuid4()
        self.transaction_id = uuid4()
        self.created_at = datetime(
            year=2026,
            month=7,
            day=20,
            hour=12,
            minute=30,
            second=45,
            tzinfo=UTC,
        )

    def test_should_create_deposit(self) -> None:
        """Deve criar um depósito com direção de crédito."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.DEPOSIT,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.CREDIT,
        )
        self.assertEqual(transaction.amount, self.amount)
        self.assertIsNone(transaction.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_withdrawal(self) -> None:
        """Deve criar um saque com direção de débito."""

        transaction = BankrollTransactionFactory.create_withdrawal(
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.WITHDRAWAL,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.DEBIT,
        )
        self.assertEqual(transaction.amount, self.amount)
        self.assertIsNone(transaction.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_stake_reservation(self) -> None:
        """Deve criar uma reserva de stake vinculada ao contrato."""

        transaction = BankrollTransactionFactory.reserve_stake(
            amount=self.amount,
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.STAKE_RESERVED,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.DEBIT,
        )
        self.assertEqual(transaction.amount, self.amount)
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_stake_release(self) -> None:
        """Deve criar uma liberação de stake vinculada ao contrato."""

        transaction = BankrollTransactionFactory.release_stake(
            amount=self.amount,
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.STAKE_RELEASED,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.CREDIT,
        )
        self.assertEqual(transaction.amount, self.amount)
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_win_settlement(self) -> None:
        """Deve criar uma liquidação WIN com retorno total em crédito."""

        gross_return = Decimal("180.00")

        transaction = BankrollTransactionFactory.settle_win(
            amount=gross_return,
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_WIN,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.CREDIT,
        )
        self.assertEqual(transaction.amount, gross_return)
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_loss_settlement(self) -> None:
        """Deve registrar LOSS como entrada neutra de valor zero."""

        transaction = BankrollTransactionFactory.settle_loss(
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_LOSS,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.NEUTRAL,
        )
        self.assertEqual(transaction.amount, Decimal("0"))
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_draw_settlement(self) -> None:
        """Deve criar liquidação DRAW devolvendo a stake."""

        refunded_stake = Decimal("100.00")

        transaction = BankrollTransactionFactory.settle_draw(
            amount=refunded_stake,
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertIsInstance(transaction, BankrollTransaction)
        self.assertIs(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_DRAW,
        )
        self.assertIs(
            transaction.direction,
            BankrollTransactionDirection.CREDIT,
        )
        self.assertEqual(transaction.amount, refunded_stake)
        self.assertEqual(transaction.contract_id, self.contract_id)
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_create_credit_with_positive_signed_amount(self) -> None:
        """Depósito deve produzir valor assinado positivo."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertEqual(transaction.signed_amount, self.amount)
        self.assertTrue(transaction.affects_balance)

    def test_should_create_debit_with_negative_signed_amount(self) -> None:
        """Saque deve produzir valor assinado negativo."""

        transaction = BankrollTransactionFactory.create_withdrawal(
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertEqual(transaction.signed_amount, -self.amount)
        self.assertTrue(transaction.affects_balance)

    def test_should_create_neutral_loss_with_zero_signed_amount(
        self,
    ) -> None:
        """Liquidação LOSS deve possuir valor assinado igual a zero."""

        transaction = BankrollTransactionFactory.settle_loss(
            contract_id=self.contract_id,
            created_at=self.created_at,
        )

        self.assertEqual(transaction.signed_amount, Decimal("0"))
        self.assertFalse(transaction.affects_balance)

    def test_should_generate_unique_transaction_ids(self) -> None:
        """Deve gerar um UUID diferente para cada transação."""

        first_transaction = (
            BankrollTransactionFactory.create_deposit(
                amount=self.amount,
                created_at=self.created_at,
            )
        )
        second_transaction = (
            BankrollTransactionFactory.create_deposit(
                amount=self.amount,
                created_at=self.created_at,
            )
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

    def test_should_preserve_explicit_transaction_id(self) -> None:
        """Deve preservar exatamente o transaction_id fornecido."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            transaction_id=self.transaction_id,
            created_at=self.created_at,
        )

        self.assertEqual(
            transaction.transaction_id,
            self.transaction_id,
        )

    def test_should_generate_timezone_aware_timestamp_when_omitted(
        self,
    ) -> None:
        """Deve gerar automaticamente um timestamp UTC com timezone."""

        before_creation = datetime.now(UTC)

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
        )

        after_creation = datetime.now(UTC)

        self.assertIsInstance(transaction.created_at, datetime)
        self.assertIsNotNone(transaction.created_at.tzinfo)
        self.assertIsNotNone(transaction.created_at.utcoffset())
        self.assertEqual(transaction.created_at.utcoffset(), UTC.utcoffset(
            transaction.created_at
        ))
        self.assertGreaterEqual(
            transaction.created_at,
            before_creation,
        )
        self.assertLessEqual(
            transaction.created_at,
            after_creation,
        )

    def test_should_preserve_explicit_timestamp(self) -> None:
        """Deve preservar exatamente o timestamp fornecido."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            created_at=self.created_at,
        )

        self.assertEqual(transaction.created_at, self.created_at)
        self.assertIs(transaction.created_at, self.created_at)

    def test_should_propagate_description_and_reference(self) -> None:
        """Deve repassar os metadados opcionais para a entidade."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            description="Aporte inicial",
            reference="BANK-001",
            created_at=self.created_at,
        )

        self.assertEqual(
            transaction.description,
            "Aporte inicial",
        )
        self.assertEqual(
            transaction.reference,
            "BANK-001",
        )
        self.assertIs(
            transaction.status,
            BankrollEntryStatus.REGISTERED,
        )

    def test_should_normalize_description_and_reference(self) -> None:
        """Deve permitir que a entidade normalize os textos opcionais."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            description="  Aporte inicial  ",
            reference="  BANK-001  ",
            created_at=self.created_at,
        )

        self.assertEqual(
            transaction.description,
            "Aporte inicial",
        )
        self.assertEqual(
            transaction.reference,
            "BANK-001",
        )

    def test_should_convert_blank_optional_texts_to_none(self) -> None:
        """Deve converter textos vazios ou em branco para None."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=self.amount,
            description="   ",
            reference="",
            created_at=self.created_at,
        )

        self.assertIsNone(transaction.description)
        self.assertIsNone(transaction.reference)

    def test_should_always_use_registered_status(self) -> None:
        """Toda nova transação deve iniciar com status REGISTERED."""

        transactions = (
            BankrollTransactionFactory.create_deposit(
                amount=self.amount,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.create_withdrawal(
                amount=self.amount,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.reserve_stake(
                amount=self.amount,
                contract_id=self.contract_id,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.release_stake(
                amount=self.amount,
                contract_id=self.contract_id,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.settle_win(
                amount=Decimal("180.00"),
                contract_id=self.contract_id,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.settle_loss(
                contract_id=self.contract_id,
                created_at=self.created_at,
            ),
            BankrollTransactionFactory.settle_draw(
                amount=self.amount,
                contract_id=self.contract_id,
                created_at=self.created_at,
            ),
        )

        for transaction in transactions:
            with self.subTest(
                transaction_type=transaction.transaction_type
            ):
                self.assertIs(
                    transaction.status,
                    BankrollEntryStatus.REGISTERED,
                )

    def test_should_reject_invalid_contract_id_on_stake_reservation(
        self,
    ) -> None:
        """Deve rejeitar contract_id inválido na reserva de stake."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.reserve_stake(
                amount=self.amount,
                contract_id="invalid-id",  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_contract_id_on_stake_release(
        self,
    ) -> None:
        """Deve rejeitar contract_id inválido na liberação de stake."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.release_stake(
                amount=self.amount,
                contract_id=123,  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_contract_id_on_win_settlement(
        self,
    ) -> None:
        """Deve rejeitar contract_id inválido na liquidação WIN."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.settle_win(
                amount=self.amount,
                contract_id=123,  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_contract_id_on_loss_settlement(
        self,
    ) -> None:
        """Deve rejeitar contract_id inválido na liquidação LOSS."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.settle_loss(
                contract_id=None,  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_contract_id_on_draw_settlement(
        self,
    ) -> None:
        """Deve rejeitar contract_id inválido na liquidação DRAW."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.settle_draw(
                amount=self.amount,
                contract_id=[],  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_invalid_transaction_id(self) -> None:
        """Deve rejeitar transaction_id que não seja UUID nem None."""

        with self.assertRaises(
            InvalidBankrollTransactionReferenceError
        ):
            BankrollTransactionFactory.create_deposit(
                amount=self.amount,
                transaction_id="invalid-id",  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_non_decimal_deposit_amount(self) -> None:
        """Deve propagar a validação de tipo do valor para a entidade."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.create_deposit(
                amount=100.00,  # type: ignore[arg-type]
                created_at=self.created_at,
            )

    def test_should_reject_zero_deposit_amount(self) -> None:
        """Deve rejeitar depósito com valor igual a zero."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.create_deposit(
                amount=Decimal("0"),
                created_at=self.created_at,
            )

    def test_should_reject_negative_withdrawal_amount(self) -> None:
        """Deve rejeitar saque com valor negativo."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.create_withdrawal(
                amount=Decimal("-10.00"),
                created_at=self.created_at,
            )

    def test_should_reject_zero_stake_reservation(self) -> None:
        """Deve rejeitar reserva de stake com valor igual a zero."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.reserve_stake(
                amount=Decimal("0"),
                contract_id=self.contract_id,
                created_at=self.created_at,
            )

    def test_should_reject_non_finite_win_return(self) -> None:
        """Deve rejeitar retorno WIN com valor não finito."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.settle_win(
                amount=Decimal("NaN"),
                contract_id=self.contract_id,
                created_at=self.created_at,
            )

    def test_should_reject_infinite_draw_amount(self) -> None:
        """Deve rejeitar devolução DRAW com valor infinito."""

        with self.assertRaises(
            InvalidBankrollTransactionAmountError
        ):
            BankrollTransactionFactory.settle_draw(
                amount=Decimal("Infinity"),
                contract_id=self.contract_id,
                created_at=self.created_at,
            )

    def test_should_reject_naive_timestamp(self) -> None:
        """Deve rejeitar timestamp sem timezone."""

        naive_timestamp = datetime(
            year=2026,
            month=7,
            day=20,
            hour=12,
        )

        with self.assertRaises(
            InvalidBankrollTransactionTimestampError
        ):
            BankrollTransactionFactory.create_deposit(
                amount=self.amount,
                created_at=naive_timestamp,
            )

    def test_should_reject_incompatible_deposit_direction(
        self,
    ) -> None:
        """Deve impedir depósito criado com direção de débito."""

        with self.assertRaises(
            IncompatibleBankrollTransactionDirectionError
        ):
            BankrollTransactionFactory._create(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.DEBIT,
                amount=self.amount,
                created_at=self.created_at,
            )

    def test_should_reject_incompatible_withdrawal_direction(
        self,
    ) -> None:
        """Deve impedir saque criado com direção de crédito."""

        with self.assertRaises(
            IncompatibleBankrollTransactionDirectionError
        ):
            BankrollTransactionFactory._create(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                created_at=self.created_at,
            )

    def test_should_reject_incompatible_stake_reservation_direction(
        self,
    ) -> None:
        """Deve impedir reserva de stake com direção de crédito."""

        with self.assertRaises(
            IncompatibleBankrollTransactionDirectionError
        ):
            BankrollTransactionFactory._create(
                transaction_type=(
                    BankrollTransactionType.STAKE_RESERVED
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                contract_id=self.contract_id,
                created_at=self.created_at,
            )

    def test_should_reject_incompatible_loss_direction(self) -> None:
        """Deve impedir liquidação LOSS com direção de crédito."""

        with self.assertRaises(
            IncompatibleBankrollTransactionDirectionError
        ):
            BankrollTransactionFactory._create(
                transaction_type=(
                    BankrollTransactionType.SETTLEMENT_LOSS
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=self.amount,
                contract_id=self.contract_id,
                created_at=self.created_at,
            )

    def test_should_reject_incompatible_draw_direction(self) -> None:
        """Deve impedir liquidação DRAW com direção neutra."""

        with self.assertRaises(
            IncompatibleBankrollTransactionDirectionError
        ):
            BankrollTransactionFactory._create(
                transaction_type=(
                    BankrollTransactionType.SETTLEMENT_DRAW
                ),
                direction=BankrollTransactionDirection.NEUTRAL,
                amount=Decimal("0"),
                contract_id=self.contract_id,
                created_at=self.created_at,
            )


if __name__ == "__main__":
    unittest.main()