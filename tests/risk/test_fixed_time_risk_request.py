"""
Unit tests for the AEGIS fixed-time risk request.

These tests validate the construction rules, calculated properties,
boundary values, immutability, and value-object behavior of
``FixedTimeRiskRequest``.
"""

import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from src.risk.exceptions import (
    InvalidActiveContractsError,
    InvalidExposureError,
    InvalidPayoutError,
    InvalidStakeValueError,
)
from src.risk.fixed_time_risk_request import FixedTimeRiskRequest


class TestFixedTimeRiskRequest(unittest.TestCase):
    """Test suite for ``FixedTimeRiskRequest``."""

    def setUp(self) -> None:
        """Create valid default request values for each test."""
        self.valid_request_data = {
            "stake": Decimal("50.00"),
            "payout": Decimal("80.00"),
            "bankroll_equity": Decimal("1000.00"),
            "current_exposure": Decimal("100.00"),
            "active_contracts": 2,
        }

    def _create_request(
        self,
        **overrides: object,
    ) -> FixedTimeRiskRequest:
        """
        Create a request using valid defaults and optional overrides.

        Args:
            **overrides:
                Values that replace fields from the valid default request.

        Returns:
            A ``FixedTimeRiskRequest`` built with the resulting values.
        """
        request_data = self.valid_request_data.copy()
        request_data.update(overrides)

        return FixedTimeRiskRequest(**request_data)  # type: ignore[arg-type]

    def test_should_create_valid_request(self) -> None:
        """A request should be created when every value is valid."""
        request = self._create_request()

        self.assertEqual(request.stake, Decimal("50.00"))
        self.assertEqual(request.payout, Decimal("80.00"))
        self.assertEqual(
            request.bankroll_equity,
            Decimal("1000.00"),
        )
        self.assertEqual(
            request.current_exposure,
            Decimal("100.00"),
        )
        self.assertEqual(request.active_contracts, 2)

    def test_should_be_equal_when_all_values_are_equal(self) -> None:
        """Requests containing the same values should compare as equal."""
        first_request = self._create_request()
        second_request = self._create_request()

        self.assertEqual(first_request, second_request)

    def test_should_not_be_equal_when_values_are_different(self) -> None:
        """Requests with different values should not compare as equal."""
        first_request = self._create_request()
        second_request = self._create_request(
            active_contracts=3,
        )

        self.assertNotEqual(first_request, second_request)

    def test_should_be_hashable(self) -> None:
        """A frozen request should be usable in hash-based collections."""
        request = self._create_request()
        requests = {request}

        self.assertIn(request, requests)

    def test_should_be_immutable(self) -> None:
        """Request fields should not be modifiable after construction."""
        request = self._create_request()

        with self.assertRaises(FrozenInstanceError):
            request.stake = Decimal("75.00")  # type: ignore[misc]

    def test_should_calculate_projected_exposure(self) -> None:
        """Projected exposure should include the candidate stake."""
        request = self._create_request(
            stake=Decimal("50.00"),
            current_exposure=Decimal("100.00"),
        )

        self.assertEqual(
            request.projected_exposure,
            Decimal("150.00"),
        )

    def test_should_calculate_stake_percentage(self) -> None:
        """Stake percentage should be calculated from bankroll equity."""
        request = self._create_request(
            stake=Decimal("50.00"),
            bankroll_equity=Decimal("1000.00"),
        )

        self.assertEqual(
            request.stake_percentage,
            Decimal("5.00"),
        )

    def test_should_calculate_projected_exposure_percentage(
        self,
    ) -> None:
        """Projected exposure percentage should use projected exposure."""
        request = self._create_request(
            stake=Decimal("50.00"),
            bankroll_equity=Decimal("1000.00"),
            current_exposure=Decimal("100.00"),
        )

        self.assertEqual(
            request.projected_exposure_percentage,
            Decimal("15.00"),
        )

    def test_should_preserve_decimal_precision_in_calculations(
        self,
    ) -> None:
        """Calculated percentages should preserve Decimal arithmetic."""
        request = self._create_request(
            stake=Decimal("1"),
            bankroll_equity=Decimal("3"),
            current_exposure=Decimal("0"),
        )

        expected_percentage = (
            Decimal("1") / Decimal("3")
        ) * Decimal("100")

        self.assertEqual(
            request.stake_percentage,
            expected_percentage,
        )
        self.assertEqual(
            request.projected_exposure_percentage,
            expected_percentage,
        )

    def test_should_accept_payout_equal_to_zero(self) -> None:
        """A payout of exactly zero should be valid."""
        request = self._create_request(
            payout=Decimal("0"),
        )

        self.assertEqual(request.payout, Decimal("0"))

    def test_should_accept_payout_equal_to_100(self) -> None:
        """A payout of exactly 100 should be valid."""
        request = self._create_request(
            payout=Decimal("100"),
        )

        self.assertEqual(request.payout, Decimal("100"))

    def test_should_accept_current_exposure_equal_to_zero(self) -> None:
        """A request without current exposure should be valid."""
        request = self._create_request(
            current_exposure=Decimal("0"),
        )

        self.assertEqual(
            request.current_exposure,
            Decimal("0"),
        )
        self.assertEqual(
            request.projected_exposure,
            request.stake,
        )

    def test_should_accept_current_exposure_equal_to_bankroll_equity(
        self,
    ) -> None:
        """Current exposure equal to equity should satisfy construction."""
        request = self._create_request(
            bankroll_equity=Decimal("1000.00"),
            current_exposure=Decimal("1000.00"),
        )

        self.assertEqual(
            request.current_exposure,
            request.bankroll_equity,
        )

    def test_should_accept_zero_active_contracts(self) -> None:
        """Zero should be the smallest valid active-contract count."""
        request = self._create_request(
            active_contracts=0,
        )

        self.assertEqual(request.active_contracts, 0)

    def test_should_reject_stake_that_is_not_decimal(self) -> None:
        """Stake must be represented by ``Decimal``."""
        invalid_values = (
            50,
            50.0,
            "50.00",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidStakeValueError,
                    "stake must be an instance of Decimal",
                ):
                    self._create_request(
                        stake=invalid_value,
                    )

    def test_should_reject_payout_that_is_not_decimal(self) -> None:
        """Payout must be represented by ``Decimal``."""
        invalid_values = (
            80,
            80.0,
            "80.00",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidPayoutError,
                    "payout must be an instance of Decimal",
                ):
                    self._create_request(
                        payout=invalid_value,
                    )

    def test_should_reject_bankroll_equity_that_is_not_decimal(
        self,
    ) -> None:
        """Bankroll equity must be represented by ``Decimal``."""
        invalid_values = (
            1000,
            1000.0,
            "1000.00",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidExposureError,
                    (
                        "bankroll_equity must be an instance "
                        "of Decimal"
                    ),
                ):
                    self._create_request(
                        bankroll_equity=invalid_value,
                    )

    def test_should_reject_current_exposure_that_is_not_decimal(
        self,
    ) -> None:
        """Current exposure must be represented by ``Decimal``."""
        invalid_values = (
            100,
            100.0,
            "100.00",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidExposureError,
                    (
                        "current_exposure must be an instance "
                        "of Decimal"
                    ),
                ):
                    self._create_request(
                        current_exposure=invalid_value,
                    )

    def test_should_reject_non_finite_stake(self) -> None:
        """Stake must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidStakeValueError,
                    "stake must be a finite Decimal value",
                ):
                    self._create_request(
                        stake=invalid_value,
                    )

    def test_should_reject_non_finite_payout(self) -> None:
        """Payout must not be NaN or infinite."""
        invalid_values = (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidPayoutError,
                    "payout must be a finite Decimal value",
                ):
                    self._create_request(
                        payout=invalid_value,
                    )

    def test_should_reject_non_finite_bankroll_equity(self) -> None:
        """Bankroll equity must not be NaN or infinite."""
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
                        "bankroll_equity must be a finite "
                        "Decimal value"
                    ),
                ):
                    self._create_request(
                        bankroll_equity=invalid_value,
                    )

    def test_should_reject_non_finite_current_exposure(self) -> None:
        """Current exposure must not be NaN or infinite."""
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
                        "current_exposure must be a finite "
                        "Decimal value"
                    ),
                ):
                    self._create_request(
                        current_exposure=invalid_value,
                    )

    def test_should_reject_zero_stake(self) -> None:
        """Stake must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidStakeValueError,
            "stake must be greater than zero",
        ):
            self._create_request(
                stake=Decimal("0"),
            )

    def test_should_reject_negative_stake(self) -> None:
        """Stake must not be negative."""
        with self.assertRaises(InvalidStakeValueError):
            self._create_request(
                stake=Decimal("-0.01"),
            )

    def test_should_reject_negative_payout(self) -> None:
        """Payout must not be lower than zero."""
        with self.assertRaisesRegex(
            InvalidPayoutError,
            "payout must be greater than or equal to zero",
        ):
            self._create_request(
                payout=Decimal("-0.01"),
            )

    def test_should_reject_payout_above_100(self) -> None:
        """Payout must not exceed 100."""
        with self.assertRaisesRegex(
            InvalidPayoutError,
            "payout must be less than or equal to 100",
        ):
            self._create_request(
                payout=Decimal("100.01"),
            )

    def test_should_reject_zero_bankroll_equity(self) -> None:
        """Bankroll equity must be greater than zero."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            "bankroll_equity must be greater than zero",
        ):
            self._create_request(
                bankroll_equity=Decimal("0"),
            )

    def test_should_reject_negative_bankroll_equity(self) -> None:
        """Bankroll equity must not be negative."""
        with self.assertRaises(InvalidExposureError):
            self._create_request(
                bankroll_equity=Decimal("-1000.00"),
            )

    def test_should_reject_negative_current_exposure(self) -> None:
        """Current exposure must be greater than or equal to zero."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            (
                "current_exposure must be greater than or equal "
                "to zero"
            ),
        ):
            self._create_request(
                current_exposure=Decimal("-0.01"),
            )

    def test_should_reject_current_exposure_above_bankroll_equity(
        self,
    ) -> None:
        """Current exposure must not exceed bankroll equity."""
        with self.assertRaisesRegex(
            InvalidExposureError,
            (
                "current_exposure must be less than or equal "
                "to bankroll_equity"
            ),
        ):
            self._create_request(
                bankroll_equity=Decimal("1000.00"),
                current_exposure=Decimal("1000.01"),
            )

    def test_should_reject_active_contracts_that_is_not_integer(
        self,
    ) -> None:
        """Active contracts must be represented by an integer."""
        invalid_values = (
            2.0,
            Decimal("2"),
            "2",
            None,
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidActiveContractsError,
                    "active_contracts must be an integer",
                ):
                    self._create_request(
                        active_contracts=invalid_value,
                    )

    def test_should_reject_boolean_active_contracts(self) -> None:
        """Boolean values must not be accepted as contract counts."""
        for invalid_value in (True, False):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    InvalidActiveContractsError,
                    "active_contracts must be an integer",
                ):
                    self._create_request(
                        active_contracts=invalid_value,
                    )

    def test_should_reject_negative_active_contracts(self) -> None:
        """Active-contract count must not be negative."""
        with self.assertRaisesRegex(
            InvalidActiveContractsError,
            (
                "active_contracts must be greater than or equal "
                "to zero"
            ),
        ):
            self._create_request(
                active_contracts=-1,
            )


if __name__ == "__main__":
    unittest.main()