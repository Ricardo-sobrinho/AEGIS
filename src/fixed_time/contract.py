"""
AEGIS - Fixed-Time Contract Domain Entity.

This module defines the fixed-time contract entity and controls its complete
domain lifecycle.

A fixed-time contract represents an operation with:

- a predefined stake;
- a direction, CALL or PUT;
- a fixed duration;
- an expected payout;
- an entry price;
- an expiration price;
- a final result.

The entity is responsible only for protecting its own state and validating
lifecycle transitions. Financial settlement remains the responsibility of the
BankrollEngine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from src.fixed_time.enums import (
    ExecutionMode,
    FixedTimeContractResult,
    FixedTimeContractStatus,
    FixedTimeDirection,
)
from src.fixed_time.exceptions import (
    FixedTimeContractAlreadySettledError,
    InvalidFixedTimeContractError,
    InvalidFixedTimeContractTransitionError,
    InvalidPayoutError,
    InvalidStakeError,
)


@dataclass(slots=True)
class FixedTimeContract:
    """
    Represents a fixed-time trading contract.

    The contract protects its lifecycle through explicit state transitions.

    Valid primary lifecycle:

        CREATED
        -> RISK_APPROVED
        -> STAKE_RESERVED
        -> SUBMITTED
        -> ACCEPTED
        -> ACTIVE
        -> EXPIRED
        -> SETTLED

    Alternative terminal states:

        REJECTED
        CANCELLED
        FAILED

    Attributes:
        symbol:
            Financial instrument traded by the contract.

        direction:
            Contract direction, CALL or PUT.

        stake:
            Financial amount committed to the contract.

        payout:
            Expected payout associated with a winning contract.

        duration:
            Contract duration in seconds.

        strategy_id:
            Identifier of the strategy that originated the contract.

        signal_id:
            Identifier of the signal that originated the contract.

        contract_id:
            Unique internal contract identifier.

        status:
            Current lifecycle status.

        result:
            Final contract result.

        execution_mode:
            Execution environment: PAPER, DEMO or REAL.
    """

    symbol: str
    direction: FixedTimeDirection
    stake: Decimal
    payout: Decimal
    duration: int
    strategy_id: str
    signal_id: str

    contract_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    status: FixedTimeContractStatus = (
        FixedTimeContractStatus.CREATED
    )

    result: FixedTimeContractResult = (
        FixedTimeContractResult.PENDING
    )

    execution_mode: ExecutionMode = ExecutionMode.PAPER

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    risk_approved_at: datetime | None = None
    stake_reserved_at: datetime | None = None
    submitted_at: datetime | None = None
    accepted_at: datetime | None = None
    activated_at: datetime | None = None
    expired_at: datetime | None = None
    settled_at: datetime | None = None
    rejected_at: datetime | None = None
    cancelled_at: datetime | None = None
    failed_at: datetime | None = None

    broker_reference: str | None = None
    entry_price: Decimal | None = None
    expiration_price: Decimal | None = None

    rejection_reason: str | None = None
    cancellation_reason: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize the contract after creation."""
        normalized_symbol = self.symbol.strip().upper()
        normalized_strategy_id = self.strategy_id.strip()
        normalized_signal_id = self.signal_id.strip()

        if not normalized_symbol:
            raise InvalidFixedTimeContractError(
                "Contract symbol cannot be empty."
            )

        if not isinstance(
            self.direction,
            FixedTimeDirection,
        ):
            raise InvalidFixedTimeContractError(
                "Contract direction must be a FixedTimeDirection."
            )

        if not isinstance(self.stake, Decimal):
            raise InvalidStakeError(
                "Contract stake must be a Decimal."
            )

        if self.stake <= Decimal("0"):
            raise InvalidStakeError(
                "Contract stake must be greater than zero."
            )

        if not isinstance(self.payout, Decimal):
            raise InvalidPayoutError(
                "Contract payout must be a Decimal."
            )

        if self.payout <= Decimal("0"):
            raise InvalidPayoutError(
                "Contract payout must be greater than zero."
            )

        if isinstance(self.duration, bool) or not isinstance(
            self.duration,
            int,
        ):
            raise InvalidFixedTimeContractError(
                "Contract duration must be an integer."
            )

        if self.duration <= 0:
            raise InvalidFixedTimeContractError(
                "Contract duration must be greater than zero."
            )

        if not normalized_strategy_id:
            raise InvalidFixedTimeContractError(
                "Strategy ID cannot be empty."
            )

        if not normalized_signal_id:
            raise InvalidFixedTimeContractError(
                "Signal ID cannot be empty."
            )

        if not isinstance(
            self.execution_mode,
            ExecutionMode,
        ):
            raise InvalidFixedTimeContractError(
                "Execution mode must be an ExecutionMode."
            )

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )
        object.__setattr__(
            self,
            "strategy_id",
            normalized_strategy_id,
        )
        object.__setattr__(
            self,
            "signal_id",
            normalized_signal_id,
        )

    @property
    def is_terminal(self) -> bool:
        """Return whether the contract reached a terminal state."""
        return self.status in {
            FixedTimeContractStatus.SETTLED,
            FixedTimeContractStatus.REJECTED,
            FixedTimeContractStatus.CANCELLED,
            FixedTimeContractStatus.FAILED,
        }

    @property
    def is_pending(self) -> bool:
        """Return whether the contract result remains pending."""
        return self.result is FixedTimeContractResult.PENDING

    @property
    def is_call(self) -> bool:
        """Return whether the contract direction is CALL."""
        return self.direction is FixedTimeDirection.CALL

    @property
    def is_put(self) -> bool:
        """Return whether the contract direction is PUT."""
        return self.direction is FixedTimeDirection.PUT

    def approve_risk(self) -> None:
        """
        Mark the contract as approved by the risk layer.

        Valid transition:
            CREATED -> RISK_APPROVED
        """
        self._ensure_status(
            FixedTimeContractStatus.CREATED,
        )

        self.status = FixedTimeContractStatus.RISK_APPROVED
        self.risk_approved_at = datetime.now(UTC)

    def reserve_stake(self) -> None:
        """
        Mark the contract stake as reserved.

        Valid transition:
            RISK_APPROVED -> STAKE_RESERVED
        """
        self._ensure_status(
            FixedTimeContractStatus.RISK_APPROVED,
        )

        self.status = FixedTimeContractStatus.STAKE_RESERVED
        self.stake_reserved_at = datetime.now(UTC)

    def submit(self) -> None:
        """
        Mark the contract as submitted for execution.

        Valid transition:
            STAKE_RESERVED -> SUBMITTED
        """
        self._ensure_status(
            FixedTimeContractStatus.STAKE_RESERVED,
        )

        self.status = FixedTimeContractStatus.SUBMITTED
        self.submitted_at = datetime.now(UTC)

    def accept(
        self,
        broker_reference: str,
        entry_price: Decimal,
    ) -> None:
        """
        Mark the contract as accepted by the execution adapter.

        Args:
            broker_reference:
                External reference returned by the broker or paper adapter.

            entry_price:
                Contract entry price.

        Valid transition:
            SUBMITTED -> ACCEPTED
        """
        self._ensure_status(
            FixedTimeContractStatus.SUBMITTED,
        )

        normalized_reference = broker_reference.strip()

        if not normalized_reference:
            raise InvalidFixedTimeContractError(
                "Broker reference cannot be empty."
            )

        self._validate_positive_price(
            entry_price,
            "Entry price",
        )

        self.broker_reference = normalized_reference
        self.entry_price = entry_price
        self.accepted_at = datetime.now(UTC)
        self.status = FixedTimeContractStatus.ACCEPTED

    def activate(self) -> None:
        """
        Mark the accepted contract as active.

        Valid transition:
            ACCEPTED -> ACTIVE
        """
        self._ensure_status(
            FixedTimeContractStatus.ACCEPTED,
        )

        if self.broker_reference is None:
            raise InvalidFixedTimeContractError(
                "An accepted contract must have a broker reference."
            )

        if self.entry_price is None:
            raise InvalidFixedTimeContractError(
                "An accepted contract must have an entry price."
            )

        self.status = FixedTimeContractStatus.ACTIVE
        self.activated_at = datetime.now(UTC)

    def expire(
        self,
        expiration_price: Decimal,
    ) -> None:
        """
        Mark the active contract as expired.

        Args:
            expiration_price:
                Market price observed when the contract expired.

        Valid transition:
            ACTIVE -> EXPIRED
        """
        self._ensure_status(
            FixedTimeContractStatus.ACTIVE,
        )

        self._validate_positive_price(
            expiration_price,
            "Expiration price",
        )

        self.expiration_price = expiration_price
        self.expired_at = datetime.now(UTC)
        self.status = FixedTimeContractStatus.EXPIRED

    def settle(
        self,
        result: FixedTimeContractResult,
    ) -> None:
        """
        Settle an expired contract.

        Args:
            result:
                Final result of the contract.

        Valid transition:
            EXPIRED -> SETTLED
        """
        if self.status is FixedTimeContractStatus.SETTLED:
            raise FixedTimeContractAlreadySettledError(
                f"Contract {self.contract_id} is already settled."
            )

        self._ensure_status(
            FixedTimeContractStatus.EXPIRED,
        )

        if not isinstance(
            result,
            FixedTimeContractResult,
        ):
            raise InvalidFixedTimeContractError(
                "Settlement result must be a "
                "FixedTimeContractResult."
            )

        if result in {
            FixedTimeContractResult.PENDING,
            FixedTimeContractResult.CANCELLED,
            FixedTimeContractResult.UNKNOWN,
        }:
            raise InvalidFixedTimeContractError(
                "A settled contract must have WIN, LOSS or DRAW "
                "as its final result."
            )

        self.result = result
        self.settled_at = datetime.now(UTC)
        self.status = FixedTimeContractStatus.SETTLED

    def reject(
        self,
        reason: str | None = None,
    ) -> None:
        """
        Reject a contract before it becomes accepted.

        Rejection is permitted while the operation is still being
        evaluated, reserved or submitted.
        """
        allowed_statuses = {
            FixedTimeContractStatus.CREATED,
            FixedTimeContractStatus.RISK_APPROVED,
            FixedTimeContractStatus.STAKE_RESERVED,
            FixedTimeContractStatus.SUBMITTED,
        }

        self._ensure_status_in(
            allowed_statuses,
            target_status=FixedTimeContractStatus.REJECTED,
        )

        self.rejection_reason = self._normalize_optional_reason(
            reason,
        )
        self.rejected_at = datetime.now(UTC)
        self.status = FixedTimeContractStatus.REJECTED

    def cancel(
        self,
        reason: str | None = None,
    ) -> None:
        """
        Cancel an accepted or active contract.

        Cancellation does not perform financial operations. The
        TradeLifecycleCoordinator and BankrollEngine are responsible for
        releasing or reconciling reserved funds.
        """
        allowed_statuses = {
            FixedTimeContractStatus.ACCEPTED,
            FixedTimeContractStatus.ACTIVE,
        }

        self._ensure_status_in(
            allowed_statuses,
            target_status=FixedTimeContractStatus.CANCELLED,
        )

        self.cancellation_reason = self._normalize_optional_reason(
            reason,
        )
        self.cancelled_at = datetime.now(UTC)
        self.result = FixedTimeContractResult.CANCELLED
        self.status = FixedTimeContractStatus.CANCELLED

    def fail(
        self,
        reason: str,
    ) -> None:
        """
        Mark a non-terminal contract as failed.

        A terminal contract cannot later be converted into FAILED.
        """
        if self.is_terminal:
            raise InvalidFixedTimeContractTransitionError(
                "A terminal contract cannot transition to FAILED."
            )

        normalized_reason = reason.strip()

        if not normalized_reason:
            raise InvalidFixedTimeContractError(
                "Failure reason cannot be empty."
            )

        self.failure_reason = normalized_reason
        self.failed_at = datetime.now(UTC)
        self.status = FixedTimeContractStatus.FAILED

    def determine_result(
        self,
    ) -> FixedTimeContractResult:
        """
        Determine the expected result from entry and expiration prices.

        This method calculates the result but does not settle the contract.

        Returns:
            WIN, LOSS or DRAW.

        Raises:
            InvalidFixedTimeContractError:
                When the required prices are unavailable.
        """
        if self.entry_price is None:
            raise InvalidFixedTimeContractError(
                "Entry price is required to determine the result."
            )

        if self.expiration_price is None:
            raise InvalidFixedTimeContractError(
                "Expiration price is required to determine the result."
            )

        if self.expiration_price == self.entry_price:
            return FixedTimeContractResult.DRAW

        if self.direction is FixedTimeDirection.CALL:
            if self.expiration_price > self.entry_price:
                return FixedTimeContractResult.WIN

            return FixedTimeContractResult.LOSS

        if self.expiration_price < self.entry_price:
            return FixedTimeContractResult.WIN

        return FixedTimeContractResult.LOSS

    def _ensure_status(
        self,
        expected_status: FixedTimeContractStatus,
    ) -> None:
        """
        Ensure the contract is currently in the expected status.

        Raises:
            InvalidFixedTimeContractTransitionError:
                When the current status does not match the expected status.
        """
        if self.status is not expected_status:
            raise InvalidFixedTimeContractTransitionError(
                "Invalid fixed-time contract transition: "
                f"expected status {expected_status.value}, "
                f"but current status is {self.status.value}."
            )

    def _ensure_status_in(
        self,
        allowed_statuses: set[FixedTimeContractStatus],
        target_status: FixedTimeContractStatus,
    ) -> None:
        """
        Ensure the current status belongs to a set of allowed statuses.
        """
        if self.status not in allowed_statuses:
            allowed_values = ", ".join(
                sorted(
                    status.value
                    for status in allowed_statuses
                )
            )

            raise InvalidFixedTimeContractTransitionError(
                "Invalid fixed-time contract transition: "
                f"{self.status.value} cannot transition to "
                f"{target_status.value}. Allowed source statuses: "
                f"{allowed_values}."
            )

    @staticmethod
    def _validate_positive_price(
        price: Decimal,
        field_name: str,
    ) -> None:
        """Validate a positive Decimal price."""
        if not isinstance(price, Decimal):
            raise InvalidFixedTimeContractError(
                f"{field_name} must be a Decimal."
            )

        if price <= Decimal("0"):
            raise InvalidFixedTimeContractError(
                f"{field_name} must be greater than zero."
            )

    @staticmethod
    def _normalize_optional_reason(
        reason: str | None,
    ) -> str | None:
        """Normalize an optional lifecycle reason."""
        if reason is None:
            return None

        normalized_reason = reason.strip()

        if not normalized_reason:
            return None

        return normalized_reason