"""
Fixed-time risk manager for the AEGIS risk domain.

This module contains the deterministic risk evaluator responsible for
validating a fixed-time operation request against a fixed-time risk policy.

The manager is stateless and has no side effects. It does not:

- reserve or release bankroll funds;
- modify fixed-time contracts;
- publish domain events;
- access brokers, databases, or external services;
- persist decisions;
- execute operations.

Its only responsibility is to receive a valid policy and request and return
an immutable ``FixedTimeRiskDecision``.
"""

from src.risk.exceptions import RiskEvaluationError
from src.risk.fixed_time_risk_decision import FixedTimeRiskDecision
from src.risk.fixed_time_risk_policy import FixedTimeRiskPolicy
from src.risk.fixed_time_risk_reason import FixedTimeRiskReason
from src.risk.fixed_time_risk_request import FixedTimeRiskRequest


class FixedTimeRiskManager:
    """
    Deterministic evaluator for fixed-time operation risk.

    The manager evaluates every configured rule and accumulates all rejection
    reasons instead of stopping after the first failure. This allows callers
    to receive the complete risk assessment in a single evaluation.

    Evaluation order:

    1. minimum stake;
    2. maximum absolute stake;
    3. maximum stake percentage;
    4. minimum payout;
    5. maximum projected exposure percentage;
    6. maximum active-contract count.

    Rejections are represented by stable ``FixedTimeRiskReason`` values rather
    than human-readable strings.

    The class contains no mutable state and may be safely reused across
    multiple evaluations.
    """

    def evaluate(
        self,
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
    ) -> FixedTimeRiskDecision:
        """
        Evaluate a fixed-time operation against the supplied risk policy.

        Every risk rule is evaluated independently. When no rule is violated,
        an approved decision is returned. When one or more rules are violated,
        a rejected decision containing all corresponding reason codes is
        returned.

        Args:
            policy:
                Immutable policy containing the configured risk limits.
            request:
                Immutable request containing the operation and bankroll state.

        Returns:
            An approved or rejected ``FixedTimeRiskDecision``.

        Raises:
            RiskEvaluationError:
                If ``policy`` or ``request`` is not an instance of the expected
                domain type.
        """
        self._validate_evaluation_inputs(
            policy=policy,
            request=request,
        )

        rejection_reasons: list[FixedTimeRiskReason] = []

        self._evaluate_minimum_stake(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )
        self._evaluate_maximum_stake(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )
        self._evaluate_maximum_stake_percentage(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )
        self._evaluate_minimum_payout(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )
        self._evaluate_maximum_exposure_percentage(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )
        self._evaluate_maximum_active_contracts(
            policy=policy,
            request=request,
            rejection_reasons=rejection_reasons,
        )

        if rejection_reasons:
            return FixedTimeRiskDecision.reject(*rejection_reasons)

        return FixedTimeRiskDecision.approve()

    @staticmethod
    def _validate_evaluation_inputs(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
    ) -> None:
        """
        Validate the domain objects supplied for evaluation.

        Args:
            policy:
                Candidate fixed-time risk policy.
            request:
                Candidate fixed-time risk request.

        Raises:
            RiskEvaluationError:
                If either argument is not an instance of the required type.
        """
        if not isinstance(policy, FixedTimeRiskPolicy):
            raise RiskEvaluationError(
                "policy must be an instance of FixedTimeRiskPolicy."
            )

        if not isinstance(request, FixedTimeRiskRequest):
            raise RiskEvaluationError(
                "request must be an instance of FixedTimeRiskRequest."
            )

    @staticmethod
    def _evaluate_minimum_stake(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """Reject the operation when its stake is below the minimum limit."""
        if request.stake < policy.minimum_stake:
            rejection_reasons.append(
                FixedTimeRiskReason.STAKE_BELOW_MINIMUM
            )

    @staticmethod
    def _evaluate_maximum_stake(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """Reject the operation when its stake exceeds the absolute limit."""
        if request.stake > policy.maximum_stake:
            rejection_reasons.append(
                FixedTimeRiskReason.STAKE_ABOVE_MAXIMUM
            )

    @staticmethod
    def _evaluate_maximum_stake_percentage(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """
        Reject when the stake percentage exceeds the configured limit.
        """
        if request.stake_percentage > policy.maximum_stake_percentage:
            rejection_reasons.append(
                FixedTimeRiskReason.STAKE_PERCENTAGE_ABOVE_MAXIMUM
            )

    @staticmethod
    def _evaluate_minimum_payout(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """Reject the operation when payout is below the required minimum."""
        if request.payout < policy.minimum_payout:
            rejection_reasons.append(
                FixedTimeRiskReason.PAYOUT_BELOW_MINIMUM
            )

    @staticmethod
    def _evaluate_maximum_exposure_percentage(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """
        Reject when projected exposure exceeds the configured percentage.
        """
        if (
            request.projected_exposure_percentage
            > policy.maximum_exposure_percentage
        ):
            rejection_reasons.append(
                FixedTimeRiskReason.EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM
            )

    @staticmethod
    def _evaluate_maximum_active_contracts(
        *,
        policy: FixedTimeRiskPolicy,
        request: FixedTimeRiskRequest,
        rejection_reasons: list[FixedTimeRiskReason],
    ) -> None:
        """
        Reject when another contract would exceed the simultaneous limit.

        The request represents the state before opening the candidate
        operation. Therefore, a new operation may only be approved while the
        current number of active contracts is strictly lower than the policy
        limit.
        """
        if request.active_contracts >= policy.maximum_active_contracts:
            rejection_reasons.append(
                FixedTimeRiskReason.ACTIVE_CONTRACT_LIMIT_REACHED
            )