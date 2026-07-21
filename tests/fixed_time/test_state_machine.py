"""
AEGIS - Fixed-Time Contract State Machine Tests

Valida as regras de transição de estado dos contratos
de tempo fixo.
"""

import unittest

from src.fixed_time import (
    ContractStatus,
    FixedTimeContractStateMachine,
    InvalidContractStateError,
)


class TestFixedTimeContractStateMachine(unittest.TestCase):
    """
    Testes da máquina de estados dos contratos de tempo fixo.
    """

    def test_created_can_transition_to_submitted(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.CREATED,
            new_status=ContractStatus.SUBMITTED,
        )

        self.assertEqual(
            ContractStatus.SUBMITTED,
            new_status,
        )

    def test_submitted_can_transition_to_open(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.SUBMITTED,
            new_status=ContractStatus.OPEN,
        )

        self.assertEqual(
            ContractStatus.OPEN,
            new_status,
        )

    def test_open_can_transition_to_expired(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.OPEN,
            new_status=ContractStatus.EXPIRED,
        )

        self.assertEqual(
            ContractStatus.EXPIRED,
            new_status,
        )

    def test_expired_can_transition_to_settled(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.EXPIRED,
            new_status=ContractStatus.SETTLED,
        )

        self.assertEqual(
            ContractStatus.SETTLED,
            new_status,
        )

    def test_unknown_can_transition_to_reconciling(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.UNKNOWN,
            new_status=ContractStatus.RECONCILING,
        )

        self.assertEqual(
            ContractStatus.RECONCILING,
            new_status,
        )

    def test_failed_can_transition_to_reconciling(self) -> None:
        new_status = FixedTimeContractStateMachine.transition(
            current_status=ContractStatus.FAILED,
            new_status=ContractStatus.RECONCILING,
        )

        self.assertEqual(
            ContractStatus.RECONCILING,
            new_status,
        )

    def test_created_cannot_transition_directly_to_open(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            FixedTimeContractStateMachine.transition(
                current_status=ContractStatus.CREATED,
                new_status=ContractStatus.OPEN,
            )

    def test_open_cannot_transition_directly_to_settled(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            FixedTimeContractStateMachine.transition(
                current_status=ContractStatus.OPEN,
                new_status=ContractStatus.SETTLED,
            )

    def test_settled_is_a_terminal_state(self) -> None:
        allowed_transitions = (
            FixedTimeContractStateMachine.allowed_transitions(
                ContractStatus.SETTLED
            )
        )

        self.assertEqual(
            frozenset(),
            allowed_transitions,
        )

    def test_rejected_is_a_terminal_state(self) -> None:
        allowed_transitions = (
            FixedTimeContractStateMachine.allowed_transitions(
                ContractStatus.REJECTED
            )
        )

        self.assertEqual(
            frozenset(),
            allowed_transitions,
        )

    def test_cancelled_is_a_terminal_state(self) -> None:
        allowed_transitions = (
            FixedTimeContractStateMachine.allowed_transitions(
                ContractStatus.CANCELLED
            )
        )

        self.assertEqual(
            frozenset(),
            allowed_transitions,
        )

    def test_can_transition_returns_true_for_allowed_transition(
        self,
    ) -> None:
        result = FixedTimeContractStateMachine.can_transition(
            current_status=ContractStatus.SUBMITTED,
            new_status=ContractStatus.UNKNOWN,
        )

        self.assertTrue(result)

    def test_can_transition_returns_false_for_invalid_transition(
        self,
    ) -> None:
        result = FixedTimeContractStateMachine.can_transition(
            current_status=ContractStatus.CREATED,
            new_status=ContractStatus.SETTLED,
        )

        self.assertFalse(result)

    def test_allowed_transitions_returns_expected_statuses(
        self,
    ) -> None:
        allowed_transitions = (
            FixedTimeContractStateMachine.allowed_transitions(
                ContractStatus.CREATED
            )
        )

        expected_transitions = frozenset(
            {
                ContractStatus.SUBMITTED,
                ContractStatus.REJECTED,
                ContractStatus.CANCELLED,
                ContractStatus.FAILED,
            }
        )

        self.assertEqual(
            expected_transitions,
            allowed_transitions,
        )

    def test_transition_rejects_invalid_current_status(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            FixedTimeContractStateMachine.transition(
                current_status="CREATED",  # type: ignore[arg-type]
                new_status=ContractStatus.SUBMITTED,
            )

    def test_transition_rejects_invalid_new_status(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            FixedTimeContractStateMachine.transition(
                current_status=ContractStatus.CREATED,
                new_status="SUBMITTED",  # type: ignore[arg-type]
            )

    def test_allowed_transitions_rejects_invalid_status(self) -> None:
        with self.assertRaises(InvalidContractStateError):
            FixedTimeContractStateMachine.allowed_transitions(
                "CREATED"  # type: ignore[arg-type]
            )

    def test_can_transition_returns_false_for_invalid_types(
        self,
    ) -> None:
        result = FixedTimeContractStateMachine.can_transition(
            current_status="CREATED",  # type: ignore[arg-type]
            new_status="SUBMITTED",  # type: ignore[arg-type]
        )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()