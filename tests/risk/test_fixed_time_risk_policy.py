"""
Unit tests for the AEGIS fixed-time risk policy.

These tests validate the construction rules, domain exceptions, boundary
values, immutability, and value-object behavior of
``FixedTimeRiskPolicy``.
"""

import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from src.risk.exceptions import (
    InvalidActiveContractsError,
    InvalidExposureError,
    InvalidPayoutError,
    InvalidRiskPolicyError,
    InvalidStakeValueError,
)
from src.risk.fixed_time_risk_policy import FixedTimeRiskPolicy


class TestFixedTimeRiskPolicy(unittest.TestCase):
    """Test suite for ``FixedTimeRiskPolicy``."""

    def setUp(self) -> None:
        """Create valid default policy values for each test."""
        self.valid_policy_data = {
            "minimum_stake": Decimal("1.00"),
            "maximum_stake": Decimal("100.00"),
            "maximum_stake_percentage": Decimal("5.00"),
            "minimum_payout": Decimal("70.00"),
            "maximum_exposure_percentage": Decimal("15.00"),
            "maximum_active_contracts": 3,
        }

    def _create_policy(
        self,
        **overrides: object,
    ) -> FixedTimeRiskPolicy:
        """
        Create a policy using valid defaults and optional field overrides.

        Args:
            **overrides:
                Values that replace fields from the valid default policy.

        Returns:
            A ``FixedTimeRiskPolicy`` constructed with the resulting data.
        """
        policy_data = self.valid_policy_data.copy()
        policy_data.update(overrides)

        return FixedTimeRiskPolicy(**policy_data)  # type: ignore[arg-type]

    def test_should_create_valid_policy(self) -> None:
        """A policy should be created when every value is valid."""
        policy = self._create_policy()

        self.assertEqual(policy.minimum_stake, Decimal("1.00"))
        self.assertEqual(policy.maximum_stake, Decimal("100.00"))
        self.assertEqual(
            policy.maximum_stake_percentage,
            Decimal("5.00"),
        )
        self.assertEqual(policy.minimum_payout, Decimal("70.00"))
        self.assertEqual(
            policy.maximum_exposure_percentage,
            Decimal("15.00"),
        )
        self.assertEqual(policy.maximum_active_contracts, 3)

    def test_should_be_equal_when_all_values_are_equal(self) -> None:
        """Policies with the same values should compare as equal."""
        first_policy = self._create_policy()
        second_policy = self._create_policy()

        self.assertEqual(first_policy, second_policy)

    def test_should_not_be_equal_when_values_are_different(self) -> None:
        """Policies with different values should not compare as equal."""
        first_policy = self._create_policy()
        second_policy = self._create_policy(
            maximum_active_contracts=4,
        )

        self.assertNotEqual(first_policy, second_policy)

    def test_should_be_hashable(self) -> None:
        """A frozen policy should be usable in hash-based collections."""
        policy = self._create_policy()
        policies = {policy}

        self.assertIn(policy, policies)

    def test_should_be_immutable(self) -> None:
        """Policy fields should not be modifiable after construction."""
        policy = self._create_policy()

        with self.assertRaises(FrozenInstanceError):
            policy.minimum_stake = Decimal("2.00")  # type: ignore[misc]

    def test_should_accept_maximum_stake_equal_to_minimum_stake(
        self,
    ) -> None:
        """Equal minimum and maximum stakes should form a valid policy."""
        policy = self._create_policy(
            minimum_stake=Decimal("10.00"),
            maximum_stake=Decimal("10.00"),
        )

        self.assertEqual(policy.minimum_stake, Decimal("10.00"))
        self.assertEqual(policy.maximum_stake, Decimal("10.00"))

    def test_should_accept_maximum_stake_percentage_equal_to_100(
        self,
    ) -> None:
        """A maximum stake percentage of exactly 100 should be valid."""
        policy = self._create_policy(
            maximum_stake_percentage=Decimal("100"),
        )

        self.assertEqual(
            policy.maximum_stake_percentage,
            Decimal("100"),
        )

    def test_should_accept_minimum_payout_equal_to_zero(self) -> None:
        """A minimum payout of exactly zero should be valid."""
        policy = self._create_policy(
            minimum_payout=Decimal("0"),
        )

        self.assertEqual(policy.minimum_payout, Decimal("0"))

    def test_should_accept_minimum_payout_equal_to_100(self) -> None:
        """A minimum payout of exactly 100 should be valid."""
        policy = self._create_policy(
            minimum_payout=Decimal("100"),
        )

        self.assertEqual(policy.minimum_payout, Decimal("100"))

    def test_should_accept_maximum_exposure_percentage_equal_to_100(
        self,
    ) -> None:
        """A maximum exposure percentage of exactly 100 should be valid."""
        policy = self._create_policy(
            maximum_exposure_percentage=Decimal("100"),
        )

        self.assertEqual(
            policy.maximum_exposure_percentage,
            Decimal("100"),
        )

    def test_should_accept_one_as_maximum_active_contracts(self) -> None:
        """One active contract should be the smallest valid limit."""
        policy = self._create_policy(
            maximum_active_contracts=1,
        )

        self.assertEqual(policy.maximum_active_contracts, 1)

    def test_should_reject_minimum_stake_that_is_not_decimal(self) -> None:
        """Minimum stake must be represented by ``Decimal``."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "minimum_stake must be an instance of Decimal",
        ):
            self._create_policy(minimum_stake=1.0)

    def test_should_reject_maximum_stake_that_is_not_decimal(self) -> None:
        """Maximum stake must be represented by ``Decimal``."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "maximum_stake must be an instance of Decimal",
        ):
            self._create_policy(maximum_stake=100)

    def test_should_reject_stake_percentage_that_is_not_decimal(
        self,
    ) -> None:
        """Maximum stake percentage must be represented by ``Decimal``."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "maximum_stake_percentage must be an instance of Decimal",
        ):
            self._create_policy(maximum_stake_percentage="5.00")

    def test_should_reject_minimum_payout_that_is_not_decimal(
        self,
    ) -> None:
        """Minimum payout must be represented by ``Decimal``."""
        with self.assertRaisesRegex(
            InvalidPayoutError,
            "minimum_payout must be an instance of Decimal",
        ):
            self._create_policy(minimum_payout=70.0)

    def test_should_reject_exposure_percentage_that_is_not_decimal(
        self,
    ) -> None:
        """Maximum exposure percentage must be represented by ``Decimal``."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            "maximum_exposure_percentage must be an instance of Decimal",
        ):
            self._create_policy(
                maximum_exposure_percentage="15.00",
            )

    def test_should_reject_non_finite_minimum_stake(self) -> None:
        """Minimum stake must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidStakeValueError,
                    "minimum_stake must be a finite Decimal value",
                ):
                    self._create_policy(
                        minimum_stake=invalid_value,
                    )

    def test_should_reject_non_finite_maximum_stake(self) -> None:
        """Maximum stake must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidStakeValueError,
                    "maximum_stake must be a finite Decimal value",
                ):
                    self._create_policy(
                        maximum_stake=invalid_value,
                    )

    def test_should_reject_non_finite_stake_percentage(self) -> None:
        """Maximum stake percentage must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidStakeValueError,
                    (
                        "maximum_stake_percentage must be a finite "
                        "Decimal value"
                    ),
                ):
                    self._create_policy(
                        maximum_stake_percentage=invalid_value,
                    )

    def test_should_reject_non_finite_minimum_payout(self) -> None:
        """Minimum payout must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidPayoutError,
                    "minimum_payout must be a finite Decimal value",
                ):
                    self._create_policy(
                        minimum_payout=invalid_value,
                    )

    def test_should_reject_non_finite_exposure_percentage(self) -> None:
        """Maximum exposure percentage must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidExposureError,
                    (
                        "maximum_exposure_percentage must be a finite "
                        "Decimal value"
                    ),
                ):
                    self._create_policy(
                        maximum_exposure_percentage=invalid_value,
                    )

    def test_should_reject_zero_minimum_stake(self) -> None:
        """Minimum stake must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "minimum_stake must be greater than zero",
        ):
            self._create_policy(
                minimum_stake=Decimal("0"),
            )

    def test_should_reject_negative_minimum_stake(self) -> None:
        """Minimum stake must not be negative."""
        with self.assertRaises(InvalidStakeValueError):
            self._create_policy(
                minimum_stake=Decimal("-1.00"),
            )

    def test_should_reject_zero_maximum_stake(self) -> None:
        """Maximum stake must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "maximum_stake must be greater than zero",
        ):
            self._create_policy(
                maximum_stake=Decimal("0"),
            )

    def test_should_reject_negative_maximum_stake(self) -> None:
        """Maximum stake must not be negative."""
        with self.assertRaises(InvalidStakeValueError):
            self._create_policy(
                maximum_stake=Decimal("-100.00"),
            )

    def test_should_reject_maximum_stake_below_minimum_stake(
        self,
    ) -> None:
        """Maximum stake must not be lower than minimum stake."""
        with self.assertRaisesRegex(
            InvalidRiskPolicyError,
            (
                "maximum_stake must be greater than or equal to "
                "minimum_stake"
            ),
        ):
            self._create_policy(
                minimum_stake=Decimal("10.00"),
                maximum_stake=Decimal("9.99"),
            )

    def test_should_reject_zero_maximum_stake_percentage(self) -> None:
        """Maximum stake percentage must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "maximum_stake_percentage must be greater than zero",
        ):
            self._create_policy(
                maximum_stake_percentage=Decimal("0"),
            )

    def test_should_reject_negative_maximum_stake_percentage(
        self,
    ) -> None:
        """Maximum stake percentage must not be negative."""
        with self.assertRaises(InvalidStakeValueError):
            self._create_policy(
                maximum_stake_percentage=Decimal("-0.01"),
            )

    def test_should_reject_maximum_stake_percentage_above_100(
        self,
    ) -> None:
        """Maximum stake percentage must not exceed 100."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            (
                "maximum_stake_percentage must be less than or "
                "equal to 100"
            ),
        ):
            self._create_policy(
                maximum_stake_percentage=Decimal("100.01"),
            )

    def test_should_reject_negative_minimum_payout(self) -> None:
        """Minimum payout must not be negative."""
        with self.assertRaisesRegex(
            InvalidPayoutError,
            "minimum_payout must be greater than or equal to zero",
        ):
            self._create_policy(
                minimum_payout=Decimal("-0.01"),
            )

    def test_should_reject_minimum_payout_above_100(self) -> None:
        """Minimum payout must not exceed 100."""
        with self.assertRaisesRegex(
            InvalidPayoutError,
            "minimum_payout must be less than or equal to 100",
        ):
            self._create_policy(
                minimum_payout=Decimal("100.01"),
            )

    def test_should_reject_zero_maximum_exposure_percentage(
        self,
    ) -> None:
        """Maximum exposure percentage must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            "maximum_exposure_percentage must be greater than zero",
        ):
            self._create_policy(
                maximum_exposure_percentage=Decimal("0"),
            )

    def test_should_reject_negative_maximum_exposure_percentage(
        self,
    ) -> None:
        """Maximum exposure percentage must not be negative."""
        with self.assertRaises(InvalidExposureError):
            self._create_policy(
                maximum_exposure_percentage=Decimal("-0.01"),
            )

    def test_should_reject_exposure_percentage_above_100(
        self,
    ) -> None:
        """Maximum exposure percentage must not exceed 100."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            (
                "maximum_exposure_percentage must be less than or "
                "equal to 100"
            ),
        ):
            self._create_policy(
                maximum_exposure_percentage=Decimal("100.01"),
            )

    def test_should_reject_active_contract_limit_that_is_not_integer(
        self,
    ) -> None:
        """Maximum active contracts must be represented by an integer."""
        invalid_values = (
            3.0,
            Decimal("3"),
            "3",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidActiveContractsError,
                    "maximum_active_contracts must be an integer",
                ):
                    self._create_policy(
                        maximum_active_contracts=invalid_value,
                    )

    def test_should_reject_boolean_active_contract_limit(self) -> None:
        """Boolean values must not be accepted as integer limits."""
        for invalid_value in (True, False):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidActiveContractsError,
                    "maximum_active_contracts must be an integer",
                ):
                    self._create_policy(
                        maximum_active_contracts=invalid_value,
                    )

    def test_should_reject_zero_maximum_active_contracts(self) -> None:
        """Maximum active-contract limit must be at least one."""
        with self.assertRaisesRegex(
            InvalidActiveContractsError,
            (
                "maximum_active_contracts must be greater than or "
                "equal to 1"
            ),
        ):
            self._create_policy(
                maximum_active_contracts=0,
            )

    def test_should_reject_negative_maximum_active_contracts(
        self,
    ) -> None:
        """Maximum active-contract limit must not be negative."""
        with self.assertRaises(InvalidActiveContractsError):
            self._create_policy(
                maximum_active_contracts=-1,
            )


if __name__ == "__main__":
    unittest.main()