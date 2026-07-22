"""
Tests for TradeIntent.
"""

from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal

from src.fixed_time.enums import FixedTimeDirection
from src.fixed_time.exceptions import (
    InvalidPayoutError,
    InvalidStakeError,
    InvalidTradeIntentError,
)
from src.fixed_time.trade_intent import TradeIntent


class TradeIntentTestCase(unittest.TestCase):
    """Tests for TradeIntent."""

    def setUp(self) -> None:
        """Create a valid trade intent for each test."""
        self.intent = TradeIntent(
            symbol="EURUSD",
            direction=FixedTimeDirection.CALL,
            stake=Decimal("10.00"),
            requested_payout=Decimal("0.85"),
            duration=60,
            strategy_id="strategy-001",
            signal_id="signal-001",
        )

    def test_symbol(self) -> None:
        """Trade intent must store the normalized symbol."""
        self.assertEqual(
            self.intent.symbol,
            "EURUSD",
        )

    def test_direction(self) -> None:
        """Trade intent must store its direction."""
        self.assertEqual(
            self.intent.direction,
            FixedTimeDirection.CALL,
        )

    def test_stake(self) -> None:
        """Trade intent must store its stake."""
        self.assertEqual(
            self.intent.stake,
            Decimal("10.00"),
        )

    def test_requested_payout(self) -> None:
        """Trade intent must store its requested payout."""
        self.assertEqual(
            self.intent.requested_payout,
            Decimal("0.85"),
        )

    def test_duration(self) -> None:
        """Trade intent must store its duration."""
        self.assertEqual(
            self.intent.duration,
            60,
        )

    def test_strategy_id(self) -> None:
        """Trade intent must store the originating strategy ID."""
        self.assertEqual(
            self.intent.strategy_id,
            "strategy-001",
        )

    def test_signal_id(self) -> None:
        """Trade intent must store the originating signal ID."""
        self.assertEqual(
            self.intent.signal_id,
            "signal-001",
        )

    def test_intent_id_is_generated(self) -> None:
        """Trade intent must generate a unique identifier."""
        self.assertIsInstance(
            self.intent.intent_id,
            str,
        )
        self.assertGreater(
            len(self.intent.intent_id),
            10,
        )

    def test_created_at(self) -> None:
        """Trade intent must record its creation datetime."""
        self.assertIsInstance(
            self.intent.created_at,
            datetime,
        )

    def test_is_call(self) -> None:
        """CALL intent must report is_call as true."""
        self.assertTrue(self.intent.is_call)

    def test_is_put(self) -> None:
        """CALL intent must report is_put as false."""
        self.assertFalse(self.intent.is_put)

    def test_put_intent(self) -> None:
        """PUT intent must expose the correct direction properties."""
        intent = TradeIntent(
            symbol="EURUSD",
            direction=FixedTimeDirection.PUT,
            stake=Decimal("10.00"),
            requested_payout=Decimal("0.85"),
            duration=60,
            strategy_id="strategy",
            signal_id="signal",
        )

        self.assertTrue(intent.is_put)
        self.assertFalse(intent.is_call)

    def test_invalid_stake(self) -> None:
        """Zero stake must raise InvalidStakeError."""
        with self.assertRaises(InvalidStakeError):
            TradeIntent(
                symbol="EURUSD",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("0"),
                requested_payout=Decimal("0.85"),
                duration=60,
                strategy_id="strategy",
                signal_id="signal",
            )

    def test_invalid_payout(self) -> None:
        """Negative payout must raise InvalidPayoutError."""
        with self.assertRaises(InvalidPayoutError):
            TradeIntent(
                symbol="EURUSD",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("10.00"),
                requested_payout=Decimal("-1"),
                duration=60,
                strategy_id="strategy",
                signal_id="signal",
            )

    def test_invalid_duration(self) -> None:
        """Zero duration must raise InvalidTradeIntentError."""
        with self.assertRaises(InvalidTradeIntentError):
            TradeIntent(
                symbol="EURUSD",
                direction=FixedTimeDirection.CALL,
                stake=Decimal("10.00"),
                requested_payout=Decimal("0.85"),
                duration=0,
                strategy_id="strategy",
                signal_id="signal",
            )


if __name__ == "__main__":
    unittest.main()