"""
Fixed-time risk evaluation request for the AEGIS Risk Engine.

This module defines the immutable input object consumed by the
``FixedTimeRiskManager`` when evaluating a fixed-time contract.

All financial and percentage-related values use ``Decimal`` to prevent
precision loss caused by binary floating-point arithmetic.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import TypeAlias

from src.risk.exceptions import (
    InvalidActiveContractsError,
    InvalidExposureError,
    InvalidPayoutError,
    InvalidStakeValueError,
)

RiskValidationException: TypeAlias = type[
    InvalidStakeValueError
    | InvalidPayoutError
    | InvalidExposureError
]


@dataclass(frozen=True, slots=True)
class FixedTimeRiskRequest:
    """
    Immutable input for a fixed-time risk evaluation.

    Attributes:
        stake:
            Amount proposed for the new fixed-time contract.

        payout:
            Contract payout percentage expressed from zero to one hundred.

        bankroll_equity:
            Total bankroll equity available at evaluation time.

        current_exposure:
            Amount currently exposed in active fixed-time contracts.

        active_contracts:
            Number of fixed-time contracts currently active.
    """

    stake: Decimal
    payout: Decimal
    bankroll_equity: Decimal
    current_exposure: Decimal
    active_contracts: int

    def __post_init__(self) -> None:
        """Validate all request fields after dataclass construction."""
        self._validate_decimal_field(
            field_name="stake",
            value=self.stake,
            exception_type=InvalidStakeValueError,
        )
        self._validate_decimal_field(
            field_name="payout",
            value=self.payout,
            exception_type=InvalidPayoutError,
        )
        self._validate_decimal_field(
            field_name="bankroll_equity",
            value=self.bankroll_equity,
            exception_type=InvalidExposureError,
        )
        self._validate_decimal_field(
            field_name="current_exposure",
            value=self.current_exposure,
            exception_type=InvalidExposureError,
        )

        self._validate_stake()
        self._validate_payout()
        self._validate_bankroll_equity()
        self._validate_current_exposure()
        self._validate_active_contracts()

    @property
    def projected_exposure(self) -> Decimal:
        """
        Return total exposure after including the proposed stake.

        Returns:
            Current exposure plus the candidate contract stake.
        """
        return self.current_exposure + self.stake

    @property
    def stake_percentage(self) -> Decimal:
        """
        Return the proposed stake as a percentage of bankroll equity.

        Returns:
            Percentage of bankroll equity represented by ``stake``.
        """
        return (
            self.stake
            / self.bankroll_equity
        ) * Decimal("100")

    @property
    def projected_exposure_percentage(self) -> Decimal:
        """
        Return projected exposure as a percentage of bankroll equity.

        Returns:
            Percentage of bankroll equity that would be exposed after
            accepting the proposed contract.
        """
        return (
            self.projected_exposure
            / self.bankroll_equity
        ) * Decimal("100")

    def _validate_stake(self) -> None:
        """Validate that stake is strictly greater than zero."""
        if self.stake <= Decimal("0"):
            raise InvalidStakeValueError(
                "stake must be greater than zero."
            )

    def _validate_payout(self) -> None:
        """Validate that payout is within the inclusive range 0–100."""
        if self.payout < Decimal("0"):
            raise InvalidPayoutError(
                "payout must be greater than or equal to zero."
            )

        if self.payout > Decimal("100"):
            raise InvalidPayoutError(
                "payout must be less than or equal to 100."
            )

    def _validate_bankroll_equity(self) -> None:
        """Validate that bankroll equity is strictly greater than zero."""
        if self.bankroll_equity <= Decimal("0"):
            raise InvalidExposureError(
                "bankroll_equity must be greater than zero."
            )

    def _validate_current_exposure(self) -> None:
        """
        Validate current exposure against its permitted boundaries.

        Current exposure may be zero, but it cannot be negative or exceed
        the available bankroll equity.
        """
        if self.current_exposure < Decimal("0"):
            raise InvalidExposureError(
                "current_exposure must be greater than or equal to zero."
            )

        if self.current_exposure > self.bankroll_equity:
            raise InvalidExposureError(
                "current_exposure must be less than or equal to "
                "bankroll_equity."
            )

    def _validate_active_contracts(self) -> None:
        """
        Validate the number of active fixed-time contracts.

        Boolean values are explicitly rejected because ``bool`` is a
        subclass of ``int`` in Python.
        """
        if (
            isinstance(self.active_contracts, bool)
            or not isinstance(self.active_contracts, int)
        ):
            raise InvalidActiveContractsError(
                "active_contracts must be an integer."
            )

        if self.active_contracts < 0:
            raise InvalidActiveContractsError(
                "active_contracts must be greater than or equal to zero."
            )

    @staticmethod
    def _validate_decimal_field(
        *,
        field_name: str,
        value: object,
        exception_type: RiskValidationException,
    ) -> None:
        """
        Validate that a financial field is a finite ``Decimal``.

        Args:
            field_name:
                Name used to build the domain error message.

            value:
                Field value being validated.

            exception_type:
                Specific domain exception raised when validation fails.

        Raises:
            InvalidStakeValueError:
                When a stake-related value is invalid.

            InvalidPayoutError:
                When a payout-related value is invalid.

            InvalidExposureError:
                When an exposure or bankroll-equity value is invalid.
        """
        if not isinstance(value, Decimal):
            raise exception_type(
                f"{field_name} must be an instance of Decimal."
            )

        if not value.is_finite():
            raise exception_type(
                f"{field_name} must be a finite Decimal value."
            )