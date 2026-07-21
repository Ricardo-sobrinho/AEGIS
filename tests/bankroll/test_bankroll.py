"""
AEGIS - Bankroll Engine Tests.

Valida o agregado responsável por registrar transações e alterar os
saldos disponível e reservado da banca.
"""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from src.bankroll.bankroll import BankrollEngine
from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    DuplicateBankrollTransactionError,
    InsufficientBankrollBalanceError,
    InvalidBankrollBalanceError,
    InvalidBankrollTransactionError,
    InvalidBankrollTransactionStatusError,
)
from src.bankroll.statistics import BankrollStatistics
from src.bankroll.transaction import BankrollTransaction
from src.bankroll.transaction_factory import BankrollTransactionFactory


class TestBankrollEngine(TestCase):
    """Testa o comportamento público do BankrollEngine."""

    def setUp(self) -> None:
        """Cria uma banca limpa antes de cada teste."""

        self.initial_balance = Decimal("1000.00")
        self.bankroll = BankrollEngine(
            initial_balance=self.initial_balance
        )
        self.contract_id = uuid4()

    def test_initializes_with_expected_balances(self) -> None:
        """Deve inicializar os saldos com os valores esperados."""

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0"),
        )
        self.assertEqual(
            self.bankroll.total_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(self.bankroll.ledger, ())

    def test_rejects_non_decimal_initial_balance(self) -> None:
        """Deve rejeitar saldo inicial que não seja Decimal."""

        with self.assertRaises(InvalidBankrollBalanceError):
            BankrollEngine(initial_balance=1000)  # type: ignore[arg-type]

    def test_rejects_negative_initial_balance(self) -> None:
        """Deve rejeitar saldo inicial negativo."""

        with self.assertRaises(InvalidBankrollBalanceError):
            BankrollEngine(initial_balance=Decimal("-0.01"))

    def test_rejects_non_finite_initial_balance(self) -> None:
        """Deve rejeitar saldo inicial não finito."""

        for value in (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ):
            with self.subTest(value=value):
                with self.assertRaises(InvalidBankrollBalanceError):
                    BankrollEngine(initial_balance=value)

    def test_deposit_increases_available_and_total_balance(self) -> None:
        """Depósito deve aumentar os saldos disponível e total."""

        transaction = self.bankroll.deposit(
            Decimal("250.00"),
            description="Aporte",
            reference="DEP-001",
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1250.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0"),
        )
        self.assertEqual(
            self.bankroll.total_balance,
            Decimal("1250.00"),
        )
        self.assertEqual(self.bankroll.ledger, (transaction,))
        self.assertEqual(
            transaction.transaction_type,
            BankrollTransactionType.DEPOSIT,
        )

    def test_withdrawal_reduces_available_and_total_balance(self) -> None:
        """Saque deve reduzir os saldos disponível e total."""

        transaction = self.bankroll.withdraw(
            Decimal("200.00"),
            description="Retirada",
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("800.00"),
        )
        self.assertEqual(
            self.bankroll.total_balance,
            Decimal("800.00"),
        )
        self.assertEqual(self.bankroll.ledger, (transaction,))

    def test_rejects_withdrawal_above_available_balance(self) -> None:
        """Deve rejeitar saque superior ao saldo disponível."""

        with self.assertRaises(InsufficientBankrollBalanceError):
            self.bankroll.withdraw(Decimal("1000.01"))

        self._assert_unchanged_initial_state()

    def test_reserve_stake_moves_available_to_reserved_balance(self) -> None:
        """Reserva deve mover capital sem alterar o saldo total."""

        transaction = self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("900.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("100.00"),
        )
        self.assertEqual(
            self.bankroll.total_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("100.00"),
        )
        self.assertEqual(self.bankroll.ledger, (transaction,))

    def test_accumulates_multiple_reservations_for_same_contract(
        self,
    ) -> None:
        """Deve acumular reservas vinculadas ao mesmo contrato."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )
        self.bankroll.reserve_stake(
            amount=Decimal("50.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("150.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("150.00"),
        )
        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("850.00"),
        )

    def test_tracks_reservations_by_contract(self) -> None:
        """Deve manter reservas independentes por contrato."""

        second_contract_id = uuid4()

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )
        self.bankroll.reserve_stake(
            amount=Decimal("250.00"),
            contract_id=second_contract_id,
        )

        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("100.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_for_contract(second_contract_id),
            Decimal("250.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("350.00"),
        )

    def test_rejects_reservation_above_available_balance(self) -> None:
        """Deve rejeitar reserva superior ao saldo disponível."""

        with self.assertRaises(InsufficientBankrollBalanceError):
            self.bankroll.reserve_stake(
                amount=Decimal("1000.01"),
                contract_id=self.contract_id,
            )

        self._assert_unchanged_initial_state()

    def test_release_stake_partially_restores_available_balance(
        self,
    ) -> None:
        """Liberação parcial deve reduzir somente parte da reserva."""

        self.bankroll.reserve_stake(
            amount=Decimal("200.00"),
            contract_id=self.contract_id,
        )

        self.bankroll.release_stake(
            amount=Decimal("75.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("875.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("125.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("125.00"),
        )

    def test_release_stake_fully_removes_contract_reservation(
        self,
    ) -> None:
        """Liberação total deve eliminar a reserva do contrato."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )
        self.bankroll.release_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("0"),
        )

    def test_rejects_release_above_contract_reservation(self) -> None:
        """Deve rejeitar liberação superior à reserva do contrato."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )
        original_ledger = self.bankroll.ledger

        with self.assertRaises(InsufficientBankrollBalanceError):
            self.bankroll.release_stake(
                amount=Decimal("100.01"),
                contract_id=self.contract_id,
            )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("900.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("100.00"),
        )
        self.assertEqual(self.bankroll.ledger, original_ledger)

    def test_settle_win_removes_reservation_and_credits_return(
        self,
    ) -> None:
        """WIN deve remover a reserva e creditar o retorno total."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        transaction = self.bankroll.settle_win(
            amount=Decimal("180.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1080.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_for_contract(self.contract_id),
            Decimal("0"),
        )
        self.assertEqual(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_WIN,
        )

    def test_settle_loss_removes_reservation_without_credit(
        self,
    ) -> None:
        """LOSS deve consumir a reserva sem novo débito disponível."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        transaction = self.bankroll.settle_loss(
            contract_id=self.contract_id
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("900.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0.00"),
        )
        self.assertEqual(transaction.amount, Decimal("0"))
        self.assertEqual(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_LOSS,
        )

    def test_settle_draw_removes_reservation_and_refunds_stake(
        self,
    ) -> None:
        """DRAW deve remover a reserva e devolver a stake."""

        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        transaction = self.bankroll.settle_draw(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0.00"),
        )
        self.assertEqual(
            transaction.transaction_type,
            BankrollTransactionType.SETTLEMENT_DRAW,
        )

    def test_rejects_settlement_without_contract_reservation(
        self,
    ) -> None:
        """Deve rejeitar liquidação sem reserva existente."""

        with self.assertRaises(InsufficientBankrollBalanceError):
            self.bankroll.settle_loss(
                contract_id=self.contract_id
            )

        self._assert_unchanged_initial_state()

    def test_registers_credit_adjustment(self) -> None:
        """Ajuste de crédito deve aumentar o saldo disponível."""

        transaction = self._create_transaction(
            transaction_type=(
                BankrollTransactionType.CREDIT_ADJUSTMENT
            ),
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("25.00"),
        )

        self.bankroll.register(transaction)

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1025.00"),
        )
        self.assertEqual(self.bankroll.ledger, (transaction,))

    def test_registers_debit_adjustment(self) -> None:
        """Ajuste de débito deve reduzir o saldo disponível."""

        transaction = self._create_transaction(
            transaction_type=(
                BankrollTransactionType.DEBIT_ADJUSTMENT
            ),
            direction=BankrollTransactionDirection.DEBIT,
            amount=Decimal("25.00"),
        )

        self.bankroll.register(transaction)

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("975.00"),
        )

    def test_rejects_duplicate_transaction(self) -> None:
        """Deve impedir o registro repetido da mesma transação."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=Decimal("50.00")
        )

        self.bankroll.register(transaction)
        original_balance = self.bankroll.available_balance
        original_ledger = self.bankroll.ledger

        with self.assertRaises(DuplicateBankrollTransactionError):
            self.bankroll.register(transaction)

        self.assertEqual(
            self.bankroll.available_balance,
            original_balance,
        )
        self.assertEqual(self.bankroll.ledger, original_ledger)

    def test_rejects_non_transaction_object(self) -> None:
        """Deve rejeitar objeto que não seja BankrollTransaction."""

        with self.assertRaises(InvalidBankrollTransactionError):
            self.bankroll.register(
                "invalid"  # type: ignore[arg-type]
            )

        self._assert_unchanged_initial_state()

    def test_rejects_transaction_with_non_registered_status(
        self,
    ) -> None:
        """Deve aceitar somente transações com status REGISTERED."""

        transaction = BankrollTransactionFactory.create_deposit(
            amount=Decimal("50.00")
        )
        reversed_transaction = replace(
            transaction,
            status=BankrollEntryStatus.REVERSED,
        )

        with self.assertRaises(
            InvalidBankrollTransactionStatusError
        ):
            self.bankroll.register(reversed_transaction)

        self._assert_unchanged_initial_state()

    def test_failed_registration_is_atomic(self) -> None:
        """Falha de registro não deve alterar nenhum estado interno."""

        transaction = BankrollTransactionFactory.create_withdrawal(
            amount=Decimal("1000.01")
        )

        original_available = self.bankroll.available_balance
        original_reserved = self.bankroll.reserved_balance
        original_total = self.bankroll.total_balance
        original_ledger = self.bankroll.ledger

        with self.assertRaises(InsufficientBankrollBalanceError):
            self.bankroll.register(transaction)

        self.assertEqual(
            self.bankroll.available_balance,
            original_available,
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            original_reserved,
        )
        self.assertEqual(
            self.bankroll.total_balance,
            original_total,
        )
        self.assertEqual(self.bankroll.ledger, original_ledger)

    def test_ledger_is_exposed_as_immutable_tuple(self) -> None:
        """Ledger público deve ser uma tupla imutável."""

        transaction = self.bankroll.deposit(Decimal("50.00"))
        ledger = self.bankroll.ledger

        self.assertIsInstance(ledger, tuple)
        self.assertEqual(ledger, (transaction,))

        with self.assertRaises(AttributeError):
            ledger.append(  # type: ignore[attr-defined]
                transaction
            )

    def test_ledger_transactions_are_immutable(self) -> None:
        """Transações registradas não devem permitir alteração."""

        transaction = self.bankroll.deposit(Decimal("50.00"))

        with self.assertRaises(FrozenInstanceError):
            transaction.amount = (  # type: ignore[misc]
                Decimal("500.00")
            )

    def test_reserved_for_unknown_contract_returns_zero(self) -> None:
        """Contrato sem reserva deve retornar zero."""

        self.assertEqual(
            self.bankroll.reserved_for_contract(uuid4()),
            Decimal("0"),
        )

    def test_reserved_for_contract_rejects_non_uuid(self) -> None:
        """Consulta deve rejeitar contract_id que não seja UUID."""

        with self.assertRaises(InvalidBankrollTransactionError):
            self.bankroll.reserved_for_contract(
                "invalid"  # type: ignore[arg-type]
            )

    def test_statistics_returns_consistent_snapshot(self) -> None:
        """Estatísticas devem refletir o estado atual da banca."""

        self.bankroll.deposit(Decimal("200.00"))
        self.bankroll.withdraw(Decimal("50.00"))
        self.bankroll.reserve_stake(
            amount=Decimal("100.00"),
            contract_id=self.contract_id,
        )

        statistics = self.bankroll.statistics

        self.assertIsInstance(statistics, BankrollStatistics)
        self.assertEqual(
            statistics.available_balance,
            Decimal("1050.00"),
        )
        self.assertEqual(
            statistics.reserved_balance,
            Decimal("100.00"),
        )
        self.assertEqual(
            statistics.total_balance,
            Decimal("1150.00"),
        )
        self.assertEqual(
            statistics.total_deposits,
            Decimal("200.00"),
        )
        self.assertEqual(
            statistics.total_withdrawals,
            Decimal("50.00"),
        )
        self.assertEqual(
            statistics.total_stake_reserved,
            Decimal("100.00"),
        )
        self.assertEqual(
            statistics.ledger,
            self.bankroll.ledger,
        )

    def test_statistics_is_a_snapshot(self) -> None:
        """Fotografia antiga não deve mudar após novas transações."""

        statistics = self.bankroll.statistics

        self.bankroll.deposit(Decimal("100.00"))

        self.assertEqual(
            statistics.available_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(statistics.ledger, ())
        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1100.00"),
        )
        self.assertEqual(len(self.bankroll.ledger), 1)

    def _assert_unchanged_initial_state(self) -> None:
        """Confirma que a banca continua no estado inicial."""

        self.assertEqual(
            self.bankroll.available_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.bankroll.reserved_balance,
            Decimal("0"),
        )
        self.assertEqual(
            self.bankroll.total_balance,
            Decimal("1000.00"),
        )
        self.assertEqual(self.bankroll.ledger, ())

    @staticmethod
    def _create_transaction(
        transaction_type: BankrollTransactionType,
        direction: BankrollTransactionDirection,
        amount: Decimal,
        contract_id: UUID | None = None,
    ) -> BankrollTransaction:
        """Cria uma transação estruturalmente válida para registro."""

        return BankrollTransaction(
            transaction_type=transaction_type,
            direction=direction,
            amount=amount,
            created_at=datetime.now(UTC),
            contract_id=contract_id,
        )