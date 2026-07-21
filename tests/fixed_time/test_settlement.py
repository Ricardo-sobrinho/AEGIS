"""
AEGIS - Fixed-Time Contract Settlement Tests

Valida as regras de determinação de resultado e os cálculos
financeiros dos contratos de tempo fixo.
"""

import unittest
from decimal import Decimal

from src.fixed_time import (
    ContractResult,
    FixedTimeDirection,
    FixedTimeSettlementCalculator,
    InvalidContractDirectionError,
    InvalidContractPriceError,
    InvalidPayoutError,
    InvalidStakeError,
    SettlementCalculation,
)


class TestFixedTimeSettlementCalculator(unittest.TestCase):
    """
    Testes do calculador de liquidação de contratos de tempo fixo.
    """

    def test_call_returns_win_when_expiration_price_is_higher(
        self,
    ) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.CALL,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("65100.00"),
        )

        self.assertEqual(
            ContractResult.WIN,
            calculation.result,
        )
        self.assertEqual(
            Decimal("80.0000"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("180.0000"),
            calculation.returned_amount,
        )

    def test_call_returns_loss_when_expiration_price_is_lower(
        self,
    ) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.CALL,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("64900.00"),
        )

        self.assertEqual(
            ContractResult.LOSS,
            calculation.result,
        )
        self.assertEqual(
            Decimal("-100.00"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("0"),
            calculation.returned_amount,
        )

    def test_put_returns_win_when_expiration_price_is_lower(
        self,
    ) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.PUT,
            stake=Decimal("50.00"),
            payout=Decimal("0.75"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("64950.00"),
        )

        self.assertEqual(
            ContractResult.WIN,
            calculation.result,
        )
        self.assertEqual(
            Decimal("37.5000"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("87.5000"),
            calculation.returned_amount,
        )

    def test_put_returns_loss_when_expiration_price_is_higher(
        self,
    ) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.PUT,
            stake=Decimal("50.00"),
            payout=Decimal("0.75"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("65050.00"),
        )

        self.assertEqual(
            ContractResult.LOSS,
            calculation.result,
        )
        self.assertEqual(
            Decimal("-50.00"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("0"),
            calculation.returned_amount,
        )

    def test_equal_prices_return_draw_for_call(self) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.CALL,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("65000.00"),
        )

        self.assertEqual(
            ContractResult.DRAW,
            calculation.result,
        )
        self.assertEqual(
            Decimal("0"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("100.00"),
            calculation.returned_amount,
        )

    def test_equal_prices_return_draw_for_put(self) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.PUT,
            stake=Decimal("100.00"),
            payout=Decimal("0.80"),
            entry_price=Decimal("65000.00"),
            expiration_price=Decimal("65000.00"),
        )

        self.assertEqual(
            ContractResult.DRAW,
            calculation.result,
        )
        self.assertEqual(
            Decimal("0"),
            calculation.net_profit,
        )
        self.assertEqual(
            Decimal("100.00"),
            calculation.returned_amount,
        )

    def test_calculate_returns_settlement_calculation(self) -> None:
        calculation = FixedTimeSettlementCalculator.calculate(
            direction=FixedTimeDirection.CALL,
            stake=Decimal("10.00"),
            payout=Decimal("0.90"),
            entry_price=Decimal("100.00"),
            expiration_price=Decimal("101.00"),
        )

        self.assertIsInstance(
            calculation,
            SettlementCalculation,
        )

    def test_determine_result_returns_call_win(self) -> None:
        result = FixedTimeSettlementCalculator.determine_result(
            direction=FixedTimeDirection.CALL,
            entry_price=Decimal("100.00"),
            expiration_price=Decimal("101.00"),
        )

        self.assertEqual(
            ContractResult.WIN,
            result,
        )

    def test_determine_result_returns_put_win(self) -> None:
        result = FixedTimeSettlementCalculator.determine_result(
            direction=FixedTimeDirection.PUT,
            entry_price=Decimal("100.00"),
            expiration_price=Decimal("99.00"),
        )

        self.assertEqual(
            ContractResult.WIN,
            result,
        )

    def test_calculate_financial_result_for_win(self) -> None:
        net_profit, returned_amount = (
            FixedTimeSettlementCalculator.calculate_financial_result(
                result=ContractResult.WIN,
                stake=Decimal("200.00"),
                payout=Decimal("0.85"),
            )
        )

        self.assertEqual(
            Decimal("170.0000"),
            net_profit,
        )
        self.assertEqual(
            Decimal("370.0000"),
            returned_amount,
        )

    def test_calculate_financial_result_for_loss(self) -> None:
        net_profit, returned_amount = (
            FixedTimeSettlementCalculator.calculate_financial_result(
                result=ContractResult.LOSS,
                stake=Decimal("200.00"),
                payout=Decimal("0.85"),
            )
        )

        self.assertEqual(
            Decimal("-200.00"),
            net_profit,
        )
        self.assertEqual(
            Decimal("0"),
            returned_amount,
        )

    def test_calculate_financial_result_for_draw(self) -> None:
        net_profit, returned_amount = (
            FixedTimeSettlementCalculator.calculate_financial_result(
                result=ContractResult.DRAW,
                stake=Decimal("200.00"),
                payout=Decimal("0.85"),
            )
        )

        self.assertEqual(
            Decimal("0"),
            net_profit,
        )
        self.assertEqual(
            Decimal("200.00"),
            returned_amount,
        )

    def test_invalid_direction_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractDirectionError):
            FixedTimeSettlementCalculator.calculate(
                direction="CALL",  # type: ignore[arg-type]
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_float_stake_is_rejected(self) -> None:
        with self.assertRaises(InvalidStakeError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=100.00,  # type: ignore[arg-type]
                payout=Decimal("0.80"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_zero_stake_is_rejected(self) -> None:
        with self.assertRaises(InvalidStakeError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("0"),
                payout=Decimal("0.80"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_negative_stake_is_rejected(self) -> None:
        with self.assertRaises(InvalidStakeError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("-10.00"),
                payout=Decimal("0.80"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_float_payout_is_rejected(self) -> None:
        with self.assertRaises(InvalidPayoutError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=0.80,  # type: ignore[arg-type]
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_negative_payout_is_rejected(self) -> None:
        with self.assertRaises(InvalidPayoutError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("-0.01"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_payout_above_one_is_rejected(self) -> None:
        with self.assertRaises(InvalidPayoutError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("1.01"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("65100.00"),
            )

    def test_float_entry_price_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractPriceError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                entry_price=65000.00,  # type: ignore[arg-type]
                expiration_price=Decimal("65100.00"),
            )

    def test_zero_entry_price_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractPriceError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                entry_price=Decimal("0"),
                expiration_price=Decimal("65100.00"),
            )

    def test_negative_expiration_price_is_rejected(self) -> None:
        with self.assertRaises(InvalidContractPriceError):
            FixedTimeSettlementCalculator.calculate(
                direction=FixedTimeDirection.CALL,
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
                entry_price=Decimal("65000.00"),
                expiration_price=Decimal("-1.00"),
            )

    def test_invalid_contract_result_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FixedTimeSettlementCalculator.calculate_financial_result(
                result="WIN",  # type: ignore[arg-type]
                stake=Decimal("100.00"),
                payout=Decimal("0.80"),
            )


if __name__ == "__main__":
    unittest.main()