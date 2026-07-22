"""
Fixed-time risk policy for the AEGIS risk domain.

This module defines the immutable policy object used by the
``FixedTimeRiskManager`` when evaluating fixed-time operation requests.

The policy only stores and validates configurable risk limits. It does not
evaluate operations, access the bankroll, reserve funds, publish events, or
perform any other side effect.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.risk.exceptions import (
    InvalidActiveContractsError,
    InvalidExposureError,
    InvalidPayoutError,
    InvalidRiskPolicyError,
    InvalidStakeValueError,
)

_MINIMUM_PERCENTAGE = Decimal("0")
_MAXIMUM_PERCENTAGE = Decimal("100")


@dataclass(frozen=True, slots=True)
class FixedTimeRiskPolicy:
    """
    Immutable policy containing the limits for fixed-time risk evaluation.

    Percentages are represented on a zero-to-one-hundred scale. For example,
    ``Decimal("2.5")`` represents 2.5 percent.

    Attributes:
        minimum_stake:
            Smallest stake value that may be submitted for evaluation.
        maximum_stake:
            Largest absolute stake value allowed by the policy.
        maximum_stake_percentage:
            Maximum percentage of bankroll equity that a single stake may
            represent.
        minimum_payout:
            Minimum payout percentage accepted for an operation.
        maximum_exposure_percentage:
            Maximum percentage of bankroll equity that may remain exposed in
            active contracts.
        maximum_active_contracts:
            Maximum number of contracts that may be active simultaneously.

    Raises:
        InvalidStakeValueError:
            If stake limits or the maximum stake percentage are invalid.
        InvalidPayoutError:
            If the minimum payout is invalid.
        InvalidExposureError:
            If the maximum exposure percentage is invalid.
        InvalidActiveContractsError:
            If the active-contract limit is invalid.
        InvalidRiskPolicyError:
            If the policy contains inconsistent values.
    """

    minimum_stake: Decimal
    maximum_stake: Decimal
    maximum_stake_percentage: Decimal
    minimum_payout: Decimal
    maximum_exposure_percentage: Decimal
    maximum_active_contracts: int

    def __post_init__(self) -> None:
        """
        Validate all policy limits after object initialization.

        Because the dataclass is frozen, successful construction guarantees
        that the validated policy cannot be modified afterward.
        """
        self._validate_decimal_field(
            field_name="minimum_stake",
            value=self.minimum_stake,
            exception_type=InvalidStakeValueError,
        )
        self._validate_decimal_field(
            field_name="maximum_stake",
            value=self.maximum_stake,
            exception_type=InvalidStakeValueError,
        )
        self._validate_decimal_field(
            field_name="maximum_stake_percentage",
            value=self.maximum_stake_percentage,
            exception_type=InvalidStakeValueError,
        )
        self._validate_decimal_field(
            field_name="minimum_payout",
            value=self.minimum_payout,
            exception_type=InvalidPayoutError,
        )
        self._validate_decimal_field(
            field_name="maximum_exposure_percentage",
            value=self.maximum_exposure_percentage,
            exception_type=InvalidExposureError,
        )

        self._validate_stake_limits()
        self._validate_maximum_stake_percentage()
        self._validate_minimum_payout()
        self._validate_maximum_exposure_percentage()
        self._validate_maximum_active_contracts()

    def _validate_stake_limits(self) -> None:
        """Validate absolute minimum and maximum stake limits."""
        if self.minimum_stake <= Decimal("0"):
            raise InvalidStakeValueError(
                "minimum_stake must be greater than zero."
            )

        if self.maximum_stake <= Decimal("0"):
            raise InvalidStakeValueError(
                "maximum_stake must be greater than zero."
            )

        if self.maximum_stake < self.minimum_stake:
            raise InvalidRiskPolicyError(
                "maximum_stake must be greater than or equal to "
                "minimum_stake."
            )

    def _validate_maximum_stake_percentage(self) -> None:
        """Validate the maximum bankroll percentage allowed per stake."""
        if self.maximum_stake_percentage <= _MINIMUM_PERCENTAGE:
            raise InvalidStakeValueError(
                "maximum_stake_percentage must be greater than zero."
            )

        if self.maximum_stake_percentage > _MAXIMUM_PERCENTAGE:
            raise InvalidStakeValueError(
                "maximum_stake_percentage must be less than or equal to 100."
            )

    def _validate_minimum_payout(self) -> None:
        """Validate the minimum payout percentage."""
        if self.minimum_payout < _MINIMUM_PERCENTAGE:
            raise InvalidPayoutError(
                "minimum_payout must be greater than or equal to zero."
            )

        if self.minimum_payout > _MAXIMUM_PERCENTAGE:
            raise InvalidPayoutError(
                "minimum_payout must be less than or equal to 100."
            )

    def _validate_maximum_exposure_percentage(self) -> None:
        """Validate the maximum bankroll exposure percentage."""
        if self.maximum_exposure_percentage <= _MINIMUM_PERCENTAGE:
            raise InvalidExposureError(
                "maximum_exposure_percentage must be greater than zero."
            )

        if self.maximum_exposure_percentage > _MAXIMUM_PERCENTAGE:
            raise InvalidExposureError(
                "maximum_exposure_percentage must be less than or equal "
                "to 100."
            )

    def _validate_maximum_active_contracts(self) -> None:
        """Validate the simultaneous active-contract limit."""
        if (
            isinstance(self.maximum_active_contracts, bool)
            or not isinstance(self.maximum_active_contracts, int)
        ):
            raise InvalidActiveContractsError(
                "maximum_active_contracts must be an integer."
            )

        if self.maximum_active_contracts < 1:
            raise InvalidActiveContractsError(
                "maximum_active_contracts must be greater than or equal to 1."
            )

    @staticmethod
    def _validate_decimal_field(
        *,
        field_name: str,
        value: object,
        exception_type: type[Exception],
    ) -> None:
        """
        Ensure that a policy field is represented by a finite Decimal.

        Args:
            field_name:
                Name of the field being validated.
            value:
                Value supplied during policy construction.
            exception_type:
                Domain exception raised when validation fails.

        Raises:
            Exception:
                The domain exception received through ``exception_type``.
        """
        if not isinstance(value, Decimal):
            raise exception_type(
                f"{field_name} must be an instance of Decimal."
            )

        if not value.is_finite():
            raise exception_type(
                f"{field_name} must be a finite Decimal value."
            )