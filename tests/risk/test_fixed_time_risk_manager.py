"""
Unit tests for the AEGIS fixed-time risk manager.

These tests validate the complete risk-evaluation behavior of
``FixedTimeRiskManager``, including approvals, individual rejection
rules, multiple simultaneous reasons, boundary conditions,
determinism, and stateless operation.
"""

import unittest
from decimal import Decimal

from src.risk.fixed_time_risk_decision import FixedTimeRiskDecision
from src.risk.fixed_time_risk_manager import FixedTimeRiskManager
from src.risk.fixed_time_risk_policy import FixedTimeRiskPolicy
from src.risk.fixed_time_risk_reason import FixedTimeRiskReason
from src.risk.fixed_time_risk_request import FixedTimeRiskRequest


class TestFixedTimeRiskManager(unittest.TestCase):
    """Test suite for ``FixedTimeRiskManager``."""

    def setUp(self) -> None:
        """Create a risk manager and a valid default policy."""
        self.manager = FixedTimeRiskManager()

        self.policy = FixedTimeRiskPolicy(
            minimum_stake=Decimal("10.00"),
            maximum_stake=Decimal("200.00"),
            maximum_stake_percentage=Decimal("10.00"),
            minimum_payout=Decimal("70.00"),
            maximum_exposure_percentage=Decimal("30.00"),
            maximum_active_contracts=3,
        )

    def _create_request(
        self,
        *,
        stake: Decimal = Decimal("50.00"),
        payout: Decimal = Decimal("80.00"),
        bankroll_equity: Decimal = Decimal("1000.00"),
        current_exposure: Decimal = Decimal("100.00"),
        active_contracts: int = 1,
    ) -> FixedTimeRiskRequest:
        """Create a request with valid defaults and optional overrides."""
        return FixedTimeRiskRequest(
            stake=stake,
            payout=payout,
            bankroll_equity=bankroll_equity,
            current_exposure=current_exposure,
            active_contracts=active_contracts,
        )

    def _evaluate(
        self,
        request: FixedTimeRiskRequest,
        policy: FixedTimeRiskPolicy | None = None,
    ) -> FixedTimeRiskDecision:
        """Evaluate a request using the supplied or default policy."""
        return self.manager.evaluate(
            request=request,
            policy=policy or self.policy,
        )

    def test_should_approve_valid_request(self) -> None:
        """A request satisfying every rule should be approved."""
        decision = self._evaluate(self._create_request())

        self.assertIsInstance(
            decision,
            FixedTimeRiskDecision,
        )
        self.assertTrue(decision.approved)
        self.assertFalse(decision.rejected)
        self.assertEqual(decision.reasons, ())

    def test_should_reject_stake_below_minimum(self) -> None:
        """Stake below the configured minimum should be rejected."""
        request = self._create_request(
            stake=Decimal("9.99"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (FixedTimeRiskReason.STAKE_BELOW_MINIMUM,),
        )

    def test_should_accept_stake_equal_to_minimum(self) -> None:
        """Stake equal to the configured minimum should be accepted."""
        request = self._create_request(
            stake=Decimal("10.00"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_reject_stake_above_maximum(self) -> None:
        """Stake above the configured maximum should be rejected."""
        isolated_policy = FixedTimeRiskPolicy(
            minimum_stake=Decimal("10.00"),
            maximum_stake=Decimal("200.00"),
            maximum_stake_percentage=Decimal("100.00"),
            minimum_payout=Decimal("70.00"),
            maximum_exposure_percentage=Decimal("100.00"),
            maximum_active_contracts=3,
        )
        request = self._create_request(
            stake=Decimal("200.01"),
            current_exposure=Decimal("0"),
        )

        decision = self._evaluate(
            request,
            isolated_policy,
        )

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,),
        )

    def test_should_accept_stake_equal_to_maximum(self) -> None:
        """Stake equal to the configured maximum should be accepted."""
        policy = FixedTimeRiskPolicy(
            minimum_stake=Decimal("10.00"),
            maximum_stake=Decimal("200.00"),
            maximum_stake_percentage=Decimal("25.00"),
            minimum_payout=Decimal("70.00"),
            maximum_exposure_percentage=Decimal("50.00"),
            maximum_active_contracts=3,
        )
        request = self._create_request(
            stake=Decimal("200.00"),
            current_exposure=Decimal("0"),
        )

        decision = self._evaluate(request, policy)

        self.assertTrue(decision.approved)

    def test_should_reject_stake_percentage_above_maximum(
        self,
    ) -> None:
        """Stake exceeding the equity percentage limit should fail."""
        request = self._create_request(
            stake=Decimal("100.01"),
            current_exposure=Decimal("0"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (
                FixedTimeRiskReason
                .STAKE_PERCENTAGE_ABOVE_MAXIMUM,
            ),
        )

    def test_should_accept_stake_percentage_equal_to_maximum(
        self,
    ) -> None:
        """Stake equal to the percentage limit should be accepted."""
        request = self._create_request(
            stake=Decimal("100.00"),
            current_exposure=Decimal("0"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_reject_payout_below_minimum(self) -> None:
        """Payout below the configured minimum should be rejected."""
        request = self._create_request(
            payout=Decimal("69.99"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,),
        )

    def test_should_accept_payout_equal_to_minimum(self) -> None:
        """Payout equal to the configured minimum should be accepted."""
        request = self._create_request(
            payout=Decimal("70.00"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_reject_projected_exposure_above_maximum(
        self,
    ) -> None:
        """Projected exposure above the policy limit should fail."""
        request = self._create_request(
            stake=Decimal("50.01"),
            current_exposure=Decimal("250.00"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (
                FixedTimeRiskReason
                .EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM,
            ),
        )

    def test_should_accept_projected_exposure_equal_to_maximum(
        self,
    ) -> None:
        """Projected exposure equal to the limit should be accepted."""
        request = self._create_request(
            stake=Decimal("50.00"),
            current_exposure=Decimal("250.00"),
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_reject_when_active_contract_limit_is_reached(
        self,
    ) -> None:
        """A new operation should fail when the limit is reached."""
        request = self._create_request(
            active_contracts=3,
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (
                FixedTimeRiskReason
                .ACTIVE_CONTRACT_LIMIT_REACHED,
            ),
        )

    def test_should_accept_one_contract_below_active_limit(
        self,
    ) -> None:
        """One available contract slot should permit evaluation."""
        request = self._create_request(
            active_contracts=2,
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_accept_zero_active_contracts(self) -> None:
        """A request without existing contracts should be accepted."""
        request = self._create_request(
            active_contracts=0,
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.approved)

    def test_should_return_all_simultaneous_rejection_reasons(
        self,
    ) -> None:
        """Every violated rule should appear in the decision."""
        request = self._create_request(
            stake=Decimal("250.00"),
            payout=Decimal("60.00"),
            bankroll_equity=Decimal("1000.00"),
            current_exposure=Decimal("800.00"),
            active_contracts=3,
        )

        decision = self._evaluate(request)

        self.assertTrue(decision.rejected)
        self.assertEqual(
            decision.reasons,
            (
                FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM,
                FixedTimeRiskReason
                .STAKE_PERCENTAGE_ABOVE_MAXIMUM,
                FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM,
                FixedTimeRiskReason
                .EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM,
                FixedTimeRiskReason
                .ACTIVE_CONTRACT_LIMIT_REACHED,
            ),
        )

    def test_should_preserve_deterministic_reason_order(
        self,
    ) -> None:
        """Reasons should always follow the domain evaluation order."""
        request = self._create_request(
            stake=Decimal("250.00"),
            payout=Decimal("60.00"),
            current_exposure=Decimal("700.00"),
            active_contracts=3,
        )

        decision = self._evaluate(request)

        self.assertEqual(
            decision.reason_codes,
            (
                "stake_above_maximum",
                "stake_percentage_above_maximum",
                "payout_below_minimum",
                "exposure_percentage_above_maximum",
                "active_contract_limit_reached",
            ),
        )

    def test_should_report_stake_below_minimum_before_other_rules(
        self,
    ) -> None:
        """Minimum-stake failure should be evaluated first."""
        request = self._create_request(
            stake=Decimal("5.00"),
            payout=Decimal("60.00"),
            current_exposure=Decimal("300.00"),
            active_contracts=3,
        )

        decision = self._evaluate(request)

        self.assertEqual(
            decision.primary_reason,
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
        )

    def test_should_not_return_duplicate_reasons(self) -> None:
        """Each violated risk rule should appear only once."""
        request = self._create_request(
            stake=Decimal("250.00"),
            payout=Decimal("60.00"),
            current_exposure=Decimal("700.00"),
            active_contracts=3,
        )

        decision = self._evaluate(request)

        self.assertEqual(
            len(decision.reasons),
            len(set(decision.reasons)),
        )

    def test_should_be_deterministic(self) -> None:
        """The same request and policy should produce equal results."""
        request = self._create_request(
            payout=Decimal("60.00"),
        )

        first_decision = self._evaluate(request)
        second_decision = self._evaluate(request)

        self.assertEqual(
            first_decision,
            second_decision,
        )

    def test_should_be_idempotent_across_many_evaluations(
        self,
    ) -> None:
        """Repeated evaluations should remain identical."""
        request = self._create_request(
            stake=Decimal("250.00"),
            payout=Decimal("60.00"),
            current_exposure=Decimal("700.00"),
            active_contracts=3,
        )

        decisions = tuple(
            self._evaluate(request)
            for _ in range(10)
        )

        for decision in decisions[1:]:
            self.assertEqual(decision, decisions[0])

    def test_should_not_modify_request(self) -> None:
        """Risk evaluation must not mutate the supplied request."""
        request = self._create_request()

        original_values = (
            request.stake,
            request.payout,
            request.bankroll_equity,
            request.current_exposure,
            request.active_contracts,
        )

        self._evaluate(request)

        self.assertEqual(
            (
                request.stake,
                request.payout,
                request.bankroll_equity,
                request.current_exposure,
                request.active_contracts,
            ),
            original_values,
        )

    def test_should_not_modify_policy(self) -> None:
        """Risk evaluation must not mutate the supplied policy."""
        original_values = (
            self.policy.minimum_stake,
            self.policy.maximum_stake,
            self.policy.maximum_stake_percentage,
            self.policy.minimum_payout,
            self.policy.maximum_exposure_percentage,
            self.policy.maximum_active_contracts,
        )

        self._evaluate(self._create_request())

        self.assertEqual(
            (
                self.policy.minimum_stake,
                self.policy.maximum_stake,
                self.policy.maximum_stake_percentage,
                self.policy.minimum_payout,
                self.policy.maximum_exposure_percentage,
                self.policy.maximum_active_contracts,
            ),
            original_values,
        )

    def test_manager_should_not_retain_evaluation_state(
        self,
    ) -> None:
        """One evaluation must not influence a later evaluation."""
        rejected_request = self._create_request(
            payout=Decimal("60.00"),
        )
        approved_request = self._create_request()

        rejected_decision = self._evaluate(rejected_request)
        approved_decision = self._evaluate(approved_request)

        self.assertTrue(rejected_decision.rejected)
        self.assertTrue(approved_decision.approved)

    def test_different_policies_should_produce_independent_results(
        self,
    ) -> None:
        """The decision should depend only on request and policy."""
        request = self._create_request(
            stake=Decimal("50.00"),
        )
        restrictive_policy = FixedTimeRiskPolicy(
            minimum_stake=Decimal("60.00"),
            maximum_stake=Decimal("200.00"),
            maximum_stake_percentage=Decimal("10.00"),
            minimum_payout=Decimal("70.00"),
            maximum_exposure_percentage=Decimal("30.00"),
            maximum_active_contracts=3,
        )

        default_decision = self._evaluate(
            request,
            self.policy,
        )
        restrictive_decision = self._evaluate(
            request,
            restrictive_policy,
        )

        self.assertTrue(default_decision.approved)
        self.assertTrue(restrictive_decision.rejected)
        self.assertEqual(
            restrictive_decision.primary_reason,
            FixedTimeRiskReason.STAKE_BELOW_MINIMUM,
        )

    def test_should_use_decimal_precision_for_stake_percentage(
        self,
    ) -> None:
        """Percentage comparisons should preserve Decimal precision."""
        policy = FixedTimeRiskPolicy(
            minimum_stake=Decimal("1.00"),
            maximum_stake=Decimal("500.00"),
            maximum_stake_percentage=Decimal("10.00"),
            minimum_payout=Decimal("70.00"),
            maximum_exposure_percentage=Decimal("50.00"),
            maximum_active_contracts=3,
        )
        request = self._create_request(
            stake=Decimal("33.334"),
            bankroll_equity=Decimal("333.33"),
            current_exposure=Decimal("0"),
        )

        decision = self._evaluate(request, policy)

        self.assertTrue(decision.rejected)
        self.assertTrue(
            decision.has_reason(
                FixedTimeRiskReason
                .STAKE_PERCENTAGE_ABOVE_MAXIMUM
            )
        )

    def test_should_use_projected_not_current_exposure(
        self,
    ) -> None:
        """Exposure evaluation should include the candidate stake."""
        request = self._create_request(
            stake=Decimal("50.01"),
            current_exposure=Decimal("250.00"),
        )

        self.assertEqual(
            request.current_exposure,
            Decimal("250.00"),
        )
        self.assertEqual(
            request.projected_exposure,
            Decimal("300.01"),
        )

        decision = self._evaluate(request)

        self.assertTrue(
            decision.has_reason(
                FixedTimeRiskReason
                .EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM
            )
        )

    def test_should_return_fixed_time_risk_decision_for_rejection(
        self,
    ) -> None:
        """Rejected evaluations should return the decision object."""
        request = self._create_request(
            payout=Decimal("60.00"),
        )

        decision = self._evaluate(request)

        self.assertIsInstance(
            decision,
            FixedTimeRiskDecision,
        )
        self.assertTrue(decision.rejected)

    def test_approved_decision_should_have_no_primary_reason(
        self,
    ) -> None:
        """An approved evaluation should expose no rejection reason."""
        decision = self._evaluate(self._create_request())

        self.assertIsNone(decision.primary_reason)
        self.assertEqual(decision.reason_codes, ())


if __name__ == "__main__":
    unittest.main()