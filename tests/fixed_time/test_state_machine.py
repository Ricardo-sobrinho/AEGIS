"""
AEGIS - Fixed-Time Contract Lifecycle Tests.

This module validates the lifecycle transitions controlled directly by the
FixedTimeContract domain entity.

The FixedTimeContract is the single authority responsible for protecting its
own lifecycle. A separate state machine must not duplicate these rules.
"""

import unittest
from decimal import Decimal

from src.fixed_time import (
    FixedTimeContract,
    FixedTimeContractAlreadySettledError,
    FixedTimeContractResult,
    FixedTimeContractStatus,
    FixedTimeDirection,
    InvalidFixedTimeContractTransitionError,
)


class TestFixedTimeContractLifecycle(unittest.TestCase):
    """
    Tests the lifecycle transitions of a fixed-time contract.
    """

    def setUp(self) -> None:
        """
        Create a valid contract in the initial CREATED state.
        """

        self.contract = FixedTimeContract(
            symbol="BTCUSDT",
            direction=FixedTimeDirection.CALL,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            duration=60,
            strategy_id="strategy-001",
            signal_id="signal-001",
        )

    def _move_to_submitted(self) -> None:
        """
        Advance the contract to the SUBMITTED state.
        """

        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

    def _move_to_accepted(self) -> None:
        """
        Advance the contract to the ACCEPTED state.
        """

        self._move_to_submitted()

        self.contract.accept(
            broker_reference="broker-reference-001",
            entry_price=Decimal("65000.00"),
        )

    def _move_to_active(self) -> None:
        """
        Advance the contract to the ACTIVE state.
        """

        self._move_to_accepted()
        self.contract.activate()

    def _move_to_expired(self) -> None:
        """
        Advance the contract to the EXPIRED state.
        """

        self._move_to_active()

        self.contract.expire(
            expiration_price=Decimal("65100.00"),
        )

    def _move_to_settled(self) -> None:
        """
        Advance the contract to the SETTLED state.
        """

        self._move_to_expired()

        self.contract.settle(
            result=FixedTimeContractResult.WIN,
        )

    def test_contract_starts_in_created_state(self) -> None:
        """
        A new contract must start in CREATED.
        """

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

        self.assertEqual(
            FixedTimeContractResult.PENDING,
            self.contract.result,
        )

        self.assertFalse(
            self.contract.is_terminal,
        )

        self.assertTrue(
            self.contract.is_pending,
        )

    def test_created_can_transition_to_risk_approved(self) -> None:
        """
        CREATED must transition to RISK_APPROVED.
        """

        self.contract.approve_risk()

        self.assertEqual(
            FixedTimeContractStatus.RISK_APPROVED,
            self.contract.status,
        )

        self.assertIsNotNone(
            self.contract.risk_approved_at,
        )

    def test_risk_approved_can_transition_to_stake_reserved(
        self,
    ) -> None:
        """
        RISK_APPROVED must transition to STAKE_RESERVED.
        """

        self.contract.approve_risk()
        self.contract.reserve_stake()

        self.assertEqual(
            FixedTimeContractStatus.STAKE_RESERVED,
            self.contract.status,
        )

        self.assertIsNotNone(
            self.contract.stake_reserved_at,
        )

    def test_stake_reserved_can_transition_to_submitted(
        self,
    ) -> None:
        """
        STAKE_RESERVED must transition to SUBMITTED.
        """

        self.contract.approve_risk()
        self.contract.reserve_stake()
        self.contract.submit()

        self.assertEqual(
            FixedTimeContractStatus.SUBMITTED,
            self.contract.status,
        )

        self.assertIsNotNone(
            self.contract.submitted_at,
        )

    def test_submitted_can_transition_to_accepted(self) -> None:
        """
        SUBMITTED must transition to ACCEPTED.
        """

        self._move_to_submitted()

        self.contract.accept(
            broker_reference="broker-reference-001",
            entry_price=Decimal("65000.00"),
        )

        self.assertEqual(
            FixedTimeContractStatus.ACCEPTED,
            self.contract.status,
        )

        self.assertEqual(
            "broker-reference-001",
            self.contract.broker_reference,
        )

        self.assertEqual(
            Decimal("65000.00"),
            self.contract.entry_price,
        )

        self.assertIsNotNone(
            self.contract.accepted_at,
        )

    def test_accepted_can_transition_to_active(self) -> None:
        """
        ACCEPTED must transition to ACTIVE.
        """

        self._move_to_accepted()
        self.contract.activate()

        self.assertEqual(
            FixedTimeContractStatus.ACTIVE,
            self.contract.status,
        )

        self.assertIsNotNone(
            self.contract.activated_at,
        )

    def test_active_can_transition_to_expired(self) -> None:
        """
        ACTIVE must transition to EXPIRED.
        """

        self._move_to_active()

        self.contract.expire(
            expiration_price=Decimal("65100.00"),
        )

        self.assertEqual(
            FixedTimeContractStatus.EXPIRED,
            self.contract.status,
        )

        self.assertEqual(
            Decimal("65100.00"),
            self.contract.expiration_price,
        )

        self.assertIsNotNone(
            self.contract.expired_at,
        )

    def test_expired_can_transition_to_settled(self) -> None:
        """
        EXPIRED must transition to SETTLED.
        """

        self._move_to_expired()

        self.contract.settle(
            result=FixedTimeContractResult.WIN,
        )

        self.assertEqual(
            FixedTimeContractStatus.SETTLED,
            self.contract.status,
        )

        self.assertEqual(
            FixedTimeContractResult.WIN,
            self.contract.result,
        )

        self.assertIsNotNone(
            self.contract.settled_at,
        )

        self.assertTrue(
            self.contract.is_terminal,
        )

        self.assertFalse(
            self.contract.is_pending,
        )

    def test_complete_lifecycle_reaches_settled(self) -> None:
        """
        The complete successful lifecycle must reach SETTLED.
        """

        self._move_to_settled()

        self.assertEqual(
            FixedTimeContractStatus.SETTLED,
            self.contract.status,
        )

        self.assertEqual(
            FixedTimeContractResult.WIN,
            self.contract.result,
        )

        self.assertTrue(
            self.contract.is_terminal,
        )

    def test_created_cannot_transition_directly_to_submitted(
        self,
    ) -> None:
        """
        CREATED cannot skip risk approval and stake reservation.
        """

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.submit()

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

    def test_created_cannot_transition_directly_to_accepted(
        self,
    ) -> None:
        """
        CREATED cannot transition directly to ACCEPTED.
        """

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.accept(
                broker_reference="broker-reference-001",
                entry_price=Decimal("65000.00"),
            )

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

    def test_created_cannot_transition_directly_to_active(
        self,
    ) -> None:
        """
        CREATED cannot transition directly to ACTIVE.
        """

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.activate()

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

    def test_created_cannot_transition_directly_to_expired(
        self,
    ) -> None:
        """
        CREATED cannot transition directly to EXPIRED.
        """

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.expire(
                expiration_price=Decimal("65100.00"),
            )

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

    def test_created_cannot_transition_directly_to_settled(
        self,
    ) -> None:
        """
        CREATED cannot transition directly to SETTLED.
        """

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.settle(
                result=FixedTimeContractResult.WIN,
            )

        self.assertEqual(
            FixedTimeContractStatus.CREATED,
            self.contract.status,
        )

    def test_risk_cannot_be_approved_twice(self) -> None:
        """
        Risk approval cannot occur more than once.
        """

        self.contract.approve_risk()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.approve_risk()

        self.assertEqual(
            FixedTimeContractStatus.RISK_APPROVED,
            self.contract.status,
        )

    def test_stake_cannot_be_reserved_twice(self) -> None:
        """
        Stake reservation cannot occur more than once.
        """

        self.contract.approve_risk()
        self.contract.reserve_stake()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.reserve_stake()

        self.assertEqual(
            FixedTimeContractStatus.STAKE_RESERVED,
            self.contract.status,
        )

    def test_contract_cannot_be_submitted_twice(self) -> None:
        """
        A contract cannot be submitted more than once.
        """

        self._move_to_submitted()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.submit()

        self.assertEqual(
            FixedTimeContractStatus.SUBMITTED,
            self.contract.status,
        )

    def test_contract_cannot_be_accepted_twice(self) -> None:
        """
        A contract cannot be accepted more than once.
        """

        self._move_to_accepted()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.accept(
                broker_reference="broker-reference-002",
                entry_price=Decimal("65010.00"),
            )

        self.assertEqual(
            FixedTimeContractStatus.ACCEPTED,
            self.contract.status,
        )

        self.assertEqual(
            "broker-reference-001",
            self.contract.broker_reference,
        )

        self.assertEqual(
            Decimal("65000.00"),
            self.contract.entry_price,
        )

    def test_contract_cannot_be_activated_twice(self) -> None:
        """
        A contract cannot be activated more than once.
        """

        self._move_to_active()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.activate()

        self.assertEqual(
            FixedTimeContractStatus.ACTIVE,
            self.contract.status,
        )

    def test_contract_cannot_be_expired_twice(self) -> None:
        """
        A contract cannot expire more than once.
        """

        self._move_to_expired()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.expire(
                expiration_price=Decimal("65200.00"),
            )

        self.assertEqual(
            FixedTimeContractStatus.EXPIRED,
            self.contract.status,
        )

        self.assertEqual(
            Decimal("65100.00"),
            self.contract.expiration_price,
        )

    def test_contract_cannot_be_settled_twice(self) -> None:
        """
        A settled contract is terminal and cannot be settled again.
        """

        self._move_to_settled()

        with self.assertRaises(
            FixedTimeContractAlreadySettledError
        ):
            self.contract.settle(
                result=FixedTimeContractResult.LOSS,
            )

        self.assertEqual(
            FixedTimeContractStatus.SETTLED,
            self.contract.status,
        )

        self.assertEqual(
            FixedTimeContractResult.WIN,
            self.contract.result,
        )

    def test_active_contract_cannot_be_settled_before_expiration(
        self,
    ) -> None:
        """
        ACTIVE must pass through EXPIRED before settlement.
        """

        self._move_to_active()

        with self.assertRaises(
            InvalidFixedTimeContractTransitionError
        ):
            self.contract.settle(
                result=FixedTimeContractResult.WIN,
            )

        self.assertEqual(
            FixedTimeContractStatus.ACTIVE,
            self.contract.status,
        )

        self.assertEqual(
            FixedTimeContractResult.PENDING,
            self.contract.result,
        )


if __name__ == "__main__":
    unittest.main()