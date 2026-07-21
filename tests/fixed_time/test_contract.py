"""
AEGIS - Fixed-Time Contract Tests

Valida a criação, as regras de negócio e o ciclo de vida completo
da entidade FixedTimeContract.
"""

import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.fixed_time import (
    ContractAlreadySettledError,
    ContractNotReadyForSettlementError,
    ContractResult,
    ContractStatus,
    FixedTimeContract,
    FixedTimeDirection,
    InvalidContractDirectionError,
    InvalidContractDurationError,
    InvalidContractPriceError,
    InvalidContractStateError,
    InvalidContractTimestampError,
    InvalidOperationalModeError,
    InvalidPayoutError,
    InvalidStakeError,
    OperationalMode,
)


class TestFixedTimeContract(unittest.TestCase):
    """
    Testes da entidade de contratos de tempo fixo.
    """

    def setUp(self) -> None:
        """
        Cria um contrato válido antes de cada teste.
        """

        self.created_at = datetime(
            2026,
            7,
            20,
            12,
            0,
            tzinfo=UTC,
        )

        self.contract = FixedTimeContract(
            symbol="btc/usdt",
            direction=FixedTimeDirection.CALL,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            duration=timedelta(minutes=1),
            mode=OperationalMode.PAPER,
            created_at=self.created_at,
        )

    def test_contract_is_created_with_expected_defaults(self) -> None:
        self.assertEqual(
            "BTCUSDT",
            self.contract.symbol,
        )
        self.assertEqual(
            ContractStatus.CREATED,
            self.contract.status,
        )
        self.assertIsNone(self.contract.result)
        self.assertIsNone(self.contract.entry_price)
        self.assertIsNone(self.contract.expiration_price)
        self.assertIsNone(self.contract.net_profit)
        self.assertIsNone(self.contract.returned_amount)
        self.assertIsNotNone(self.contract.contract_id)

    def test_symbol_is_normalized(self) -> None:
        contract = FixedTimeContract(
            symbol=" eth-usdt ",
            direction=FixedTimeDirection.PUT,
            stake=Decimal("50.00"),
            payout=Decimal("0.75"),
            duration=timedelta(minutes=5),
        )

        self.assertEqual(
            "ETHUSDT",
            contract.symbol,
        )

    def test_empty_symbol_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FixedTimeContract(
                symbol="   ",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
            )

    def test_invalid_direction_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractDirectionError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction="CALL",  # type: ignore[arg-type]
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
            )

    def test_float_stake_is_rejected(self) -> None:
        with self.assertRaises(InvalidStakeError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=100.00,  # type: ignore[arg-type]
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
            )

    def test_zero_stake_is_rejected(self) -> None:
        with self.assertRaises(InvalidStakeError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("0"),
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
            )

    def test_invalid_payout_is_rejected(self) -> None:
        with self.assertRaises(InvalidPayoutError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("1.50"),
                duration=timedelta(minutes=1),
            )

    def test_invalid_duration_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractDurationError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                duration=timedelta(0),
            )

    def test_invalid_operational_mode_is_rejected(self) -> None:
        with self.assertRaises(InvalidOperationalModeError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
                mode="PAPER",  # type: ignore[arg-type]
            )

    def test_created_at_without_timezone_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractTimestampError):
            FixedTimeContract(
                symbol="BTCUSDT",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                duration=timedelta(minutes=1),
                created_at=datetime(2026, 7, 20, 12, 0),
            )

    def test_submit_changes_status_and_records_timestamp(self) -> None:
        submitted_at = datetime(
            2026,
            7,
            20,
            12,
            1,
            tzinfo=UTC,
        )

        self.contract.submit(submitted_at=submitted_at)

        self.assertEqual(
            ContractStatus.SUBMITTED,
            self.contract.status,
        )
        self.assertEqual(
            submitted_at,
            self.contract.submitted_at,
        )

    def test_open_records_entry_and_expiration_data(self) -> None:
        submitted_at = datetime(
            2026,
            7,
            20,
            12,
            1,
            tzinfo=UTC,
        )
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )

        self.contract.submit(submitted_at=submitted_at)
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
            external_contract_id=" broker-123 ",
        )

        self.assertEqual(
            ContractStatus.OPEN,
            self.contract.status,
        )
        self.assertEqual(
            Decimal("65000.00"),
            self.contract.entry_price,
        )
        self.assertEqual(
            opened_at,
            self.contract.opened_at,
        )
        self.assertEqual(
            opened_at + timedelta(minutes=1),
            self.contract.expiration_at,
        )
        self.assertEqual(
            "broker-123",
            self.contract.external_contract_id,
        )

    def test_open_rejects_invalid_entry_price(self) -> None:
        self.contract.submit()

        with self.assertRaises(InvalidContractPriceError):
            self.contract.open(
                entry_price=Decimal("0"),
            )

    def test_contract_cannot_open_before_submit(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            self.contract.open(
                entry_price=Decimal("65000.00"),
            )

    def test_contract_cannot_expire_before_expected_time(self) -> None:
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )

        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
        )

        with self.assertRaises(InvalidContractTimestampError):
            self.contract.mark_expired(
                expired_at=opened_at + timedelta(seconds=30),
            )

    def test_call_contract_completes_with_win(self) -> None:
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )
        expired_at = opened_at + timedelta(minutes=1)

        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
        )
        self.contract.mark_expired(
            expired_at=expired_at,
        )

        result = self.contract.settle(
            expiration_price=Decimal("65100.00"),
            settled_at=expired_at,
        )

        self.assertEqual(
            ContractResult.WIN,
            result,
        )
        self.assertEqual(
            ContractStatus.SETTLED,
            self.contract.status,
        )
        self.assertEqual(
            ContractResult.WIN,
            self.contract.result,
        )
        self.assertEqual(
            Decimal("80.0000"),
            self.contract.net_profit,
        )
        self.assertEqual(
            Decimal("180.0000"),
            self.contract.returned_amount,
        )

    def test_put_contract_completes_with_win(self) -> None:
        contract = FixedTimeContract(
            symbol="ETHUSDT",
            direction=FixedTimeDirection.PUT,
            stake=Decimal("50.00"),
            payout=Decimal("0.75"),
            duration=timedelta(minutes=1),
        )

        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )
        expired_at = opened_at + timedelta(minutes=1)

        contract.submit()
        contract.open(
            entry_price=Decimal("3500.00"),
            opened_at=opened_at,
        )
        contract.mark_expired(
            expired_at=expired_at,
        )

        result = contract.settle(
            expiration_price=Decimal("3490.00"),
            settled_at=expired_at,
        )

        self.assertEqual(
            ContractResult.WIN,
            result,
        )
        self.assertEqual(
            Decimal("37.5000"),
            contract.net_profit,
        )
        self.assertEqual(
            Decimal("87.5000"),
            contract.returned_amount,
        )

    def test_contract_completes_with_loss(self) -> None:
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )
        expired_at = opened_at + timedelta(minutes=1)

        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
        )
        self.contract.mark_expired(
            expired_at=expired_at,
        )

        result = self.contract.settle(
            expiration_price=Decimal("64900.00"),
            settled_at=expired_at,
        )

        self.assertEqual(
            ContractResult.LOSS,
            result,
        )
        self.assertEqual(
            Decimal("-100.00"),
            self.contract.net_profit,
        )
        self.assertEqual(
            Decimal("0"),
            self.contract.returned_amount,
        )

    def test_contract_completes_with_draw(self) -> None:
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )
        expired_at = opened_at + timedelta(minutes=1)

        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
        )
        self.contract.mark_expired(
            expired_at=expired_at,
        )

        result = self.contract.settle(
            expiration_price=Decimal("65000.00"),
            settled_at=expired_at,
        )

        self.assertEqual(
            ContractResult.DRAW,
            result,
        )
        self.assertEqual(
            Decimal("0"),
            self.contract.net_profit,
        )
        self.assertEqual(
            Decimal("100.00"),
            self.contract.returned_amount,
        )

    def test_contract_cannot_settle_before_expiration(self) -> None:
        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
        )

        with self.assertRaises(ContractNotReadyForSettlementError):
            self.contract.settle(
                expiration_price=Decimal("65100.00"),
            )

    def test_contract_cannot_be_settled_twice(self) -> None:
        opened_at = datetime(
            2026,
            7,
            20,
            12,
            2,
            tzinfo=UTC,
        )
        expired_at = opened_at + timedelta(minutes=1)

        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
            opened_at=opened_at,
        )
        self.contract.mark_expired(
            expired_at=expired_at,
        )
        self.contract.settle(
            expiration_price=Decimal("65100.00"),
            settled_at=expired_at,
        )

        with self.assertRaises(ContractAlreadySettledError):
            self.contract.settle(
                expiration_price=Decimal("65200.00"),
                settled_at=expired_at,
            )

    def test_submitted_contract_can_be_rejected(self) -> None:
        self.contract.submit()
        self.contract.reject(" Ordem rejeitada pela plataforma ")

        self.assertEqual(
            ContractStatus.REJECTED,
            self.contract.status,
        )
        self.assertEqual(
            "Ordem rejeitada pela plataforma",
            self.contract.failure_reason,
        )

    def test_created_contract_can_be_cancelled(self) -> None:
        self.contract.cancel(" Operação cancelada pelo usuário ")

        self.assertEqual(
            ContractStatus.CANCELLED,
            self.contract.status,
        )
        self.assertEqual(
            "Operação cancelada pelo usuário",
            self.contract.failure_reason,
        )

    def test_open_contract_can_be_marked_unknown(self) -> None:
        self.contract.submit()
        self.contract.open(
            entry_price=Decimal("65000.00"),
        )
        self.contract.mark_unknown(
            "Conexão perdida durante a confirmação",
        )

        self.assertEqual(
            ContractStatus.UNKNOWN,
            self.contract.status,
        )

    def test_unknown_contract_can_enter_reconciliation(self) -> None:
        self.contract.submit()
        self.contract.mark_unknown(
            "Resposta da plataforma não confirmada",
        )
        self.contract.begin_reconciliation()

        self.assertEqual(
            ContractStatus.RECONCILING,
            self.contract.status,
        )

    def test_empty_failure_reason_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.contract.fail("   ")


if __name__ == "__main__":
    unittest.main()