"""
Fixed-time risk decision value object for the AEGIS risk domain.

This module represents the immutable result produced by the fixed-time
risk evaluation process.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.risk.exceptions import InvalidRiskDecisionError
from src.risk.fixed_time_risk_reason import FixedTimeRiskReason


@dataclass(frozen=True, slots=True)
class FixedTimeRiskDecision:
    """
    Represent the immutable result of a fixed-time risk evaluation.

    A decision can either be approved or rejected.

    Approved decisions must not contain rejection reasons. Rejected
    decisions must contain at least one unique ``FixedTimeRiskReason``.

    Attributes:
        approved:
            Indicates whether the candidate operation was approved.
        reasons:
            Ordered tuple containing the rejection reasons.
    """

    approved: bool
    reasons: tuple[FixedTimeRiskReason, ...]

    def __post_init__(self) -> None:
        """Validate the internal consistency of the decision."""
        self._validate_approved()
        self._validate_reasons_type()
        self._validate_reason_members()
        self._validate_duplicate_reasons()
        self._validate_decision_consistency()

    @property
    def rejected(self) -> bool:
        """
        Return whether the risk decision rejected the operation.

        Returns:
            ``True`` when the decision is rejected.
        """
        return not self.approved

    @property
    def primary_reason(self) -> FixedTimeRiskReason | None:
        """
        Return the first rejection reason.

        The first reason represents the primary reason identified by the
        risk evaluation process.

        Returns:
            The first rejection reason, or ``None`` for approved
            decisions.
        """
        if not self.reasons:
            return None

        return self.reasons[0]

    @property
    def reason_codes(self) -> tuple[str, ...]:
        """
        Return the string codes of all rejection reasons.

        Returns:
            An ordered tuple containing each reason's serialized value.
        """
        return tuple(reason.value for reason in self.reasons)

    def has_reason(self, reason: FixedTimeRiskReason) -> bool:
        """
        Return whether the decision contains a specific reason.

        Args:
            reason:
                Risk reason to search for.

        Returns:
            ``True`` when the supplied reason exists in the decision.
        """
        return reason in self.reasons

    @classmethod
    def approve(cls) -> FixedTimeRiskDecision:
        """
        Create an approved risk decision.

        Returns:
            A valid approved decision without rejection reasons.
        """
        return cls(
            approved=True,
            reasons=(),
        )

    @classmethod
    def reject(
        cls,
        *reasons: FixedTimeRiskReason,
    ) -> FixedTimeRiskDecision:
        """
        Create a rejected risk decision.

        Args:
            *reasons:
                One or more unique fixed-time risk reasons.

        Returns:
            A valid rejected risk decision.

        Raises:
            InvalidRiskDecisionError:
                If no reason is supplied, a reason is invalid, or the
                same reason is supplied more than once.
        """
        return cls(
            approved=False,
            reasons=reasons,
        )

    def _validate_approved(self) -> None:
        """Validate the decision status type."""
        if not isinstance(self.approved, bool):
            raise InvalidRiskDecisionError(
                "approved must be an instance of bool."
            )

    def _validate_reasons_type(self) -> None:
        """Validate the reasons collection type."""
        if not isinstance(self.reasons, tuple):
            raise InvalidRiskDecisionError(
                "reasons must be an instance of tuple."
            )

    def _validate_reason_members(self) -> None:
        """Validate every reason contained in the decision."""
        for reason in self.reasons:
            if not isinstance(reason, FixedTimeRiskReason):
                raise InvalidRiskDecisionError(
                    "Every reason must be an instance of "
                    "FixedTimeRiskReason."
                )

    def _validate_duplicate_reasons(self) -> None:
        """Ensure that each rejection reason appears only once."""
        if len(self.reasons) != len(set(self.reasons)):
            raise InvalidRiskDecisionError(
                "reasons must not contain duplicate values."
            )

    def _validate_decision_consistency(self) -> None:
        """Validate the relationship between status and reasons."""
        if self.approved and self.reasons:
            raise InvalidRiskDecisionError(
                "An approved decision must not contain rejection "
                "reasons."
            )

        if not self.approved and not self.reasons:
            raise InvalidRiskDecisionError(
                "A rejected decision must contain at least one reason."
            )