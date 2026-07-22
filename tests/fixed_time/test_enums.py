"""
Tests for fixed-time enums.
"""

import unittest

from src.fixed_time.enums import (
    ExecutionMode,
    FixedTimeContractResult,
    FixedTimeContractStatus,
    FixedTimeDirection,
)


class FixedTimeDirectionTestCase(unittest.TestCase):
    """Tests for FixedTimeDirection."""

    def test_call_value(self) -> None:
        self.assertEqual(
            FixedTimeDirection.CALL.value,
            "CALL",
        )

    def test_put_value(self) -> None:
        self.assertEqual(
            FixedTimeDirection.PUT.value,
            "PUT",
        )

    def test_direction_count(self) -> None:
        self.assertEqual(
            len(FixedTimeDirection),
            2,
        )


class FixedTimeContractStatusTestCase(unittest.TestCase):
    """Tests for FixedTimeContractStatus."""

    def test_created_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.CREATED.value,
            "CREATED",
        )

    def test_risk_approved_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.RISK_APPROVED.value,
            "RISK_APPROVED",
        )

    def test_stake_reserved_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.STAKE_RESERVED.value,
            "STAKE_RESERVED",
        )

    def test_submitted_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.SUBMITTED.value,
            "SUBMITTED",
        )

    def test_accepted_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.ACCEPTED.value,
            "ACCEPTED",
        )

    def test_active_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.ACTIVE.value,
            "ACTIVE",
        )

    def test_expired_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.EXPIRED.value,
            "EXPIRED",
        )

    def test_settled_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.SETTLED.value,
            "SETTLED",
        )

    def test_rejected_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.REJECTED.value,
            "REJECTED",
        )

    def test_cancelled_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.CANCELLED.value,
            "CANCELLED",
        )

    def test_failed_value(self) -> None:
        self.assertEqual(
            FixedTimeContractStatus.FAILED.value,
            "FAILED",
        )

    def test_status_count(self) -> None:
        self.assertEqual(
            len(FixedTimeContractStatus),
            11,
        )


class FixedTimeContractResultTestCase(unittest.TestCase):
    """Tests for FixedTimeContractResult."""

    def test_pending_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.PENDING.value,
            "PENDING",
        )

    def test_win_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.WIN.value,
            "WIN",
        )

    def test_loss_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.LOSS.value,
            "LOSS",
        )

    def test_draw_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.DRAW.value,
            "DRAW",
        )

    def test_cancelled_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.CANCELLED.value,
            "CANCELLED",
        )

    def test_unknown_value(self) -> None:
        self.assertEqual(
            FixedTimeContractResult.UNKNOWN.value,
            "UNKNOWN",
        )

    def test_result_count(self) -> None:
        self.assertEqual(
            len(FixedTimeContractResult),
            6,
        )


class ExecutionModeTestCase(unittest.TestCase):
    """Tests for ExecutionMode."""

    def test_paper_value(self) -> None:
        self.assertEqual(
            ExecutionMode.PAPER.value,
            "PAPER",
        )

    def test_demo_value(self) -> None:
        self.assertEqual(
            ExecutionMode.DEMO.value,
            "DEMO",
        )

    def test_real_value(self) -> None:
        self.assertEqual(
            ExecutionMode.REAL.value,
            "REAL",
        )

    def test_execution_mode_count(self) -> None:
        self.assertEqual(
            len(ExecutionMode),
            3,
        )


if __name__ == "__main__":
    unittest.main()