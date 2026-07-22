"""
Unit tests for the AEGIS fixed-time risk decision.

These tests validate the construction rules, factory methods, calculated
properties, reason handling, immutability, and value-object behavior of
``FixedTimeRiskDecision``.
"""

import unittest
from dataclasses import FrozenInstanceError

from src.risk.exceptions import InvalidRiskDecisionError
from src.risk.fixed_time_risk_decision import FixedTimeRiskDecision
from src.risk.fixed_time_risk_reason import FixedTimeRiskReason


class TestFixedTimeRiskDecision(unittest.TestCase):
    """Test suite for ``FixedTimeRiskDecision``."""

    def test_should_create_approved_decision(self) -> None:
        """An approved decision should contain no rejection reasons."""
        decision = FixedTimeRiskDecision(
            approved=True,
            reasons=(),
        )

        self.assertTrue(decision.approved)
        self.assertFalse(decision.rejected)
        self.assertEqual(decision.reasons, ())
        self.assertIsNone(decision.primary_reason)
        self.assertEqual(decision.reason_codes, ())

    def test_should_create_rejected_decision_with_one_reason(
        self,
    ) -> None:
        """A rejected decision should accept one valid reason."""
        reason = FixedTimeRiskReason.STAKE_BELOW_MINIMUM

        decision = FixedTimeRiskDecision(
            approved=False,
            reasons=(reason,),
        )

        self.assertFalse(decision.approved)
        self.assertTrue(decision.rejected)
        self.assertEqual(decision.reasons, (reason,))
        self.assertEqual(decision.primary_reason, reason)
        self.assertEqual(
            decision.reason_codes,
            (reason.value,),
        )

    def test_should_create_rejected_decision_with_multiple_reasons(
        self,
    ) -> None:
        """A rejected decision should preserve multiple valid reasons."""
        reasons = (
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
            FixedTimeRiskReason.ACTIVE_CONTRACT_LIMIT_REACHED,
        )

        decision = FixedTimeRiskDecision(
            approved=False,
            reasons=reasons,
        )

        self.assertFalse(decision.approved)
        self.assertTrue(decision.rejected)
        self.assertEqual(decision.reasons, reasons)
        self.assertEqual(decision.primary_reason, reasons[0])
        self.assertEqual(
            decision.reason_codes,
            tuple(reason.value for reason in reasons),
        )

    def test_approve_factory_should_create_approved_decision(
        self,
    ) -> None:
        """The approve factory should return a valid approval."""
        decision = FixedTimeRiskDecision.approve()

        self.assertTrue(decision.approved)
        self.assertFalse(decision.rejected)
        self.assertEqual(decision.reasons, ())
        self.assertIsNone(decision.primary_reason)
        self.assertEqual(decision.reason_codes, ())

    def test_reject_factory_should_create_rejected_decision(
        self,
    ) -> None:
        """The reject factory should preserve all supplied reasons."""
        reasons = (
            FixedTimeRiskReason.STAKE_PERCENTAGE_ABOVE_MAXIMUM,
            FixedTimeRiskReason.EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM,
        )

        decision = FixedTimeRiskDecision.reject(*reasons)

        self.assertFalse(decision.approved)
        self.assertTrue(decision.rejected)
        self.assertEqual(decision.reasons, reasons)
        self.assertEqual(decision.primary_reason, reasons[0])

    def test_should_return_first_reason_as_primary_reason(
        self,
    ) -> None:
        """Primary reason should be the first rejection reason."""
        first_reason = FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM
        second_reason = (
            FixedTimeRiskReason.ACTIVE_CONTRACT_LIMIT_REACHED
        )

        decision = FixedTimeRiskDecision.reject(
            first_reason,
            second_reason,
        )

        self.assertEqual(
            decision.primary_reason,
            first_reason,
        )

    def test_should_return_none_as_primary_reason_when_approved(
        self,
    ) -> None:
        """Approved decisions should not have a primary reason."""
        decision = FixedTimeRiskDecision.approve()

        self.assertIsNone(decision.primary_reason)

    def test_should_return_reason_codes_in_original_order(
        self,
    ) -> None:
        """Reason codes should preserve the reason evaluation order."""
        reasons = (
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
            FixedTimeRiskReason.EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM,
        )

        decision = FixedTimeRiskDecision.reject(*reasons)

        self.assertEqual(
            decision.reason_codes,
            (
                "stake_below_minimum",
                "payout_below_minimum",
                "exposure_percentage_above_maximum",
            ),
        )

    def test_has_reason_should_return_true_for_existing_reason(
        self,
    ) -> None:
        """The decision should identify an existing reason."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )

        self.assertTrue(
            decision.has_reason(
                FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM
            )
        )

    def test_has_reason_should_return_false_for_missing_reason(
        self,
    ) -> None:
        """The decision should reject membership for absent reasons."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
        )

        self.assertFalse(
            decision.has_reason(
                FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM
            )
        )

    def test_approved_decision_should_not_have_any_reason(
        self,
    ) -> None:
        """An approved decision should report no rejection reason."""
        decision = FixedTimeRiskDecision.approve()

        for reason in FixedTimeRiskReason:
            with self.subTest(reason=reason):
                self.assertFalse(decision.has_reason(reason))

    def test_should_be_equal_when_values_are_equal(self) -> None:
        """Decisions containing the same values should compare as equal."""
        first_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )
        second_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )

        self.assertEqual(first_decision, second_decision)

    def test_should_not_be_equal_when_approval_values_differ(
        self,
    ) -> None:
        """Approval and rejection decisions should not compare as equal."""
        approved_decision = FixedTimeRiskDecision.approve()
        rejected_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )

        self.assertNotEqual(
            approved_decision,
            rejected_decision,
        )

    def test_should_not_be_equal_when_reasons_differ(self) -> None:
        """Rejected decisions with different reasons should differ."""
        first_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
        )
        second_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
        )

        self.assertNotEqual(first_decision, second_decision)

    def test_should_not_be_equal_when_reason_order_differs(
        self,
    ) -> None:
        """Reason order should be significant in decision equality."""
        first_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )
        second_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
        )

        self.assertNotEqual(first_decision, second_decision)

    def test_should_be_hashable(self) -> None:
        """A frozen decision should work in hash-based collections."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )
        decisions = {decision}

        self.assertIn(decision, decisions)

    def test_equal_decisions_should_have_equal_hashes(self) -> None:
        """Equal decision objects should produce equal hash values."""
        first_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
        )
        second_decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
        )

        self.assertEqual(
            hash(first_decision),
            hash(second_decision),
        )

    def test_should_be_immutable(self) -> None:
        """Decision fields should not be modifiable after construction."""
        decision = FixedTimeRiskDecision.approve()

        with self.assertRaises(FrozenInstanceError):
            decision.approved = False  # type: ignore[misc]

    def test_reasons_should_be_immutable_tuple(self) -> None:
        """The reasons collection should not permit item assignment."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
        )

        with self.assertRaises(TypeError):
            decision.reasons[0] = (  # type: ignore[index]
                FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM
            )

    def test_should_reject_approved_value_that_is_not_boolean(
        self,
    ) -> None:
        """The approved field must be represented by a boolean."""
        invalid_values = (
            1,
            0,
            "true",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(
                    InvalidRiskDecisionError
                ):
                    FixedTimeRiskDecision(
                        approved=invalid_value,  # type: ignore[arg-type]
                        reasons=(),
                    )

    def test_should_reject_reasons_that_are_not_tuple(
        self,
    ) -> None:
        """The reasons field must be represented by a tuple."""
        invalid_values = (
            [],
            {
                FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            },
            [
                FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            ],
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(
                    InvalidRiskDecisionError
                ):
                    FixedTimeRiskDecision(
                        approved=False,
                        reasons=invalid_value,  # type: ignore[arg-type]
                    )

    def test_should_reject_reason_that_is_not_enum_member(
        self,
    ) -> None:
        """Every rejection reason must use the domain enum."""
        invalid_values = (
            "stake_below_minimum",
            1,
            None,
            object(),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(
                    InvalidRiskDecisionError
                ):
                    FixedTimeRiskDecision(
                        approved=False,
                        reasons=(
                            invalid_value,  # type: ignore[arg-type]
                        ),
                    )

    def test_should_reject_mixed_valid_and_invalid_reasons(
        self,
    ) -> None:
        """A tuple containing any invalid reason should be rejected."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=False,
                reasons=(
                    FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
                    "payout_below_minimum",  # type: ignore[arg-type]
                ),
            )

    def test_should_reject_duplicate_reasons(self) -> None:
        """The same reason must not appear more than once."""
        duplicated_reason = (
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM
        )

        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=False,
                reasons=(
                    duplicated_reason,
                    duplicated_reason,
                ),
            )

    def test_should_reject_non_consecutive_duplicate_reasons(
        self,
    ) -> None:
        """Duplicate reasons should be detected regardless of position."""
        duplicated_reason = (
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM
        )

        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=False,
                reasons=(
                    duplicated_reason,
                    FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
                    duplicated_reason,
                ),
            )

    def test_should_reject_approved_decision_with_reason(
        self,
    ) -> None:
        """An approved decision must not contain rejection reasons."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=True,
                reasons=(
                    FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
                ),
            )

    def test_should_reject_approved_decision_with_multiple_reasons(
        self,
    ) -> None:
        """Approval must remain invalid with multiple reasons."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=True,
                reasons=(
                    FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
                    FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
                ),
            )

    def test_should_reject_rejected_decision_without_reasons(
        self,
    ) -> None:
        """A rejected decision must contain at least one reason."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision(
                approved=False,
                reasons=(),
            )

    def test_reject_factory_should_reject_empty_reason_list(
        self,
    ) -> None:
        """The reject factory must not create reasonless rejection."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision.reject()

    def test_reject_factory_should_reject_duplicate_reasons(
        self,
    ) -> None:
        """The reject factory should enforce duplicate validation."""
        reason = FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM

        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision.reject(
                reason,
                reason,
            )

    def test_reject_factory_should_reject_invalid_reason(
        self,
    ) -> None:
        """The reject factory should reject non-enum reasons."""
        with self.assertRaises(InvalidRiskDecisionError):
            FixedTimeRiskDecision.reject(
                "stake_below_minimum",  # type: ignore[arg-type]
            )

    def test_should_support_every_fixed_time_risk_reason(
        self,
    ) -> None:
        """Every domain reason should create a valid rejection."""
        for reason in FixedTimeRiskReason:
            with self.subTest(reason=reason):
                decision = FixedTimeRiskDecision.reject(reason)

                self.assertTrue(decision.rejected)
                self.assertEqual(
                    decision.primary_reason,
                    reason,
                )
                self.assertTrue(
                    decision.has_reason(reason)
                )
                self.assertEqual(
                    decision.reason_codes,
                    (reason.value,),
                )

    def test_reason_codes_should_contain_strings(self) -> None:
        """Reason codes should expose strings instead of enum objects."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
            FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
        )

        for reason_code in decision.reason_codes:
            with self.subTest(reason_code=reason_code):
                self.assertIsInstance(reason_code, str)

    def test_primary_reason_should_be_enum_member(self) -> None:
        """The primary reason should remain a domain enum member."""
        decision = FixedTimeRiskDecision.reject(
            FixedTimeRiskReason.ACTIVE_CONTRACT_LIMIT_REACHED,
        )

        self.assertIsInstance(
            decision.primary_reason,
            FixedTimeRiskReason,
        )


if __name__ == "__main__":
    unittest.main()