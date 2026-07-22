"""
Tests for FixedTimeContract.
"""

from __future__ import annotations

import unittest
from decimal import Decimal

from src.fixed_time.contract import FixedTimeContract
from src.fixed_time.enums import (
    FixedTimeContractResult,
    FixedTimeContractStatus,
    FixedTimeDirection,
)
from src.fixed_time.exceptions import (
    FixedTimeContractAlreadySettledError,
    InvalidFixedTimeContractTransitionError,
)


class FixedTimeContractTestCase(unittest.TestCase):
    """Tests for FixedTimeContract."""

    def setUp(self) -> None:
        self.contract = FixedTimeContract(
            symbol="EURUSD",
            direction=FixedTimeDirection.CALL,
            stake=Decimal("10.00"),
            payout=Decimal("18.50"),
            duration=60,
            strategy_id="strategy-001",
            signal_id="signal-001",
        )

    def test_initial_status(self) -> None:
        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.CREATED,
        )

    def test_initial_result(self) -> None:
        self.assertEqual(
            self.contract.result,
            FixedTimeContractResult.PENDING,
        )

    def test_approve_risk(self) -> None:
        self.contract.approve_risk()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.RISK_APPROVED,
        )

    def test_reserve_stake(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.STAKE_RESERVED,
        )

    def test_submit(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.SUBMITTED,
        )

    def test_accept(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER-001",
            entry_price=Decimal("1.12345"),
        )

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.ACCEPTED,
        )

        self.assertEqual(
            self.contract.broker_reference,
            "BROKER-001",
        )

        self.assertEqual(
            self.contract.entry_price,
            Decimal("1.12345"),
        )

        self.assertIsNotNone(
            self.contract.accepted_at,
        )

    def test_activate(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER",
            entry_price=Decimal("1.10"),
        )

        self.contract.activate()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.ACTIVE,
        )

        self.assertIsNotNone(
            self.contract.activated_at,
        )

    def test_expire(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER",
            entry_price=Decimal("1.10"),
        )

        self.contract.activate()

        self.contract.expire(
            expiration_price=Decimal("1.20"),
        )

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.EXPIRED,
        )

        self.assertEqual(
            self.contract.expiration_price,
            Decimal("1.20"),
        )

        self.assertIsNotNone(
            self.contract.expired_at,
        )

    def test_settle_win(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER",
            entry_price=Decimal("1.10"),
        )

        self.contract.activate()

        self.contract.expire(
            expiration_price=Decimal("1.20"),
        )

        self.contract.settle(
            FixedTimeContractResult.WIN,
        )

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.SETTLED,
        )

        self.assertEqual(
            self.contract.result,
            FixedTimeContractResult.WIN,
        )

        self.assertIsNotNone(
            self.contract.settled_at,
        )

    def test_cannot_settle_twice(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER",
            entry_price=Decimal("1.10"),
        )

        self.contract.activate()

        self.contract.expire(
            expiration_price=Decimal("1.20"),
        )

        self.contract.settle(
            FixedTimeContractResult.WIN,
        )

        with self.assertRaises(
            FixedTimeContractAlreadySettledError,
        ):
            self.contract.settle(
                FixedTimeContractResult.LOSS,
            )

    def test_reject(self) -> None:
        self.contract.reject()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.REJECTED,
        )

    def test_cancel(self) -> None:
        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.contract.accept(
            broker_reference="BROKER",
            entry_price=Decimal("1.10"),
        )

        self.contract.cancel()

        self.assertEqual(
            self.contract.status,
            FixedTimeContractStatus.CANCELLED,
        )

    def test_invalid_transition(self) -> None:
        with self.assertRaises(
            InvalidFixedTimeContractTransitionError,
        ):
            self.contract.activate()

    def test_invalid_submit(self) -> None:
        with self.assertRaises(
            InvalidFixedTimeContractTransitionError,
        ):
            self.contract.submit()


if __name__ == "__main__":
    unittest.main()