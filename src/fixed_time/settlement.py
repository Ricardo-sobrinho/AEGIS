"""
AEGIS - Fixed-Time Contract Settlement.

Defines the operational result determination and the financial
calculation rules for fixed-time contracts.

This module performs pure calculations only. It does not reserve,
credit, debit or otherwise modify the bankroll. Financial state
changes remain the exclusive responsibility of BankrollEngine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.fixed_time.enums import (
    FixedTimeContractResult,
    FixedTimeDirection,
)
from src.fixed_time.exceptions import (
    InvalidContractDirectionError,
    InvalidContractPriceError,
    InvalidPayoutError,
    InvalidStakeError,
)


@dataclass(frozen=True, slots=True)
class SettlementCalculation:
    """
    Immutable financial calculation for a fixed-time contract.

    Attributes:
        result:
            Operational result of the contract: WIN, LOSS or DRAW.

        net_profit:
            Net financial result produced by the contract.

            WIN:
                Positive profit equal to stake multiplied by payout.

            LOSS:
                Negative amount equal to the entire stake.

            DRAW:
                Zero profit or loss.

        returned_amount:
            Total amount that must be returned to the bankroll.

            WIN:
                Original stake plus net profit.

            LOSS:
                Zero.

            DRAW:
                Original stake.
    """

    result: FixedTimeContractResult
    net_profit: Decimal
    returned_amount: Decimal


class FixedTimeSettlementCalculator:
    """
    Calculates the operational and financial result of a contract.

    This service is stateless and does not mutate contract or bankroll
    objects. It can therefore be safely used by the future
    TradeLifecycleCoordinator during contract settlement.
    """

    _ZERO = Decimal("0")
    _ONE = Decimal("1")

    @classmethod
    def calculate(
        cls,
        direction: FixedTimeDirection,
        stake: Decimal,
        payout: Decimal,
        entry_price: Decimal,
        expiration_price: Decimal,
    ) -> SettlementCalculation:
        """
        Determine the result and calculate the financial amounts.

        Args:
            direction:
                Contract direction, CALL or PUT.

            stake:
                Amount committed to the contract.

            payout:
                Net profit percentage for a winning contract.

                Example:
                    Decimal("0.80") represents an 80% net payout.

            entry_price:
                Market price when the contract became active.

            expiration_price:
                Market price when the contract expired.

        Returns:
            An immutable SettlementCalculation containing the result,
            net profit and returned amount.

        Raises:
            InvalidContractDirectionError:
                If direction is not a FixedTimeDirection.

            InvalidStakeError:
                If stake is not Decimal or is not positive.

            InvalidPayoutError:
                If payout is not Decimal or is outside the valid range.

            InvalidContractPriceError:
                If entry or expiration price is invalid.
        """
        cls._validate_direction(direction)
        cls._validate_stake(stake)
        cls._validate_payout(payout)
        cls._validate_price(
            entry_price,
            "Entry price",
        )
        cls._validate_price(
            expiration_price,
            "Expiration price",
        )

        result = cls.determine_result(
            direction=direction,
            entry_price=entry_price,
            expiration_price=expiration_price,
        )

        net_profit, returned_amount = (
            cls.calculate_financial_result(
                result=result,
                stake=stake,
                payout=payout,
            )
        )

        return SettlementCalculation(
            result=result,
            net_profit=net_profit,
            returned_amount=returned_amount,
        )

    @classmethod
    def determine_result(
        cls,
        direction: FixedTimeDirection,
        entry_price: Decimal,
        expiration_price: Decimal,
    ) -> FixedTimeContractResult:
        """
        Determine whether the contract ended in WIN, LOSS or DRAW.

        CALL:
            WIN when expiration price is greater than entry price.

        PUT:
            WIN when expiration price is lower than entry price.

        DRAW:
            Entry and expiration prices are equal.
        """
        cls._validate_direction(direction)
        cls._validate_price(
            entry_price,
            "Entry price",
        )
        cls._validate_price(
            expiration_price,
            "Expiration price",
        )

        if expiration_price == entry_price:
            return FixedTimeContractResult.DRAW

        if direction is FixedTimeDirection.CALL:
            if expiration_price > entry_price:
                return FixedTimeContractResult.WIN

            return FixedTimeContractResult.LOSS

        if expiration_price < entry_price:
            return FixedTimeContractResult.WIN

        return FixedTimeContractResult.LOSS

    @classmethod
    def calculate_financial_result(
        cls,
        result: FixedTimeContractResult,
        stake: Decimal,
        payout: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """
        Calculate net profit and the amount returned to the bankroll.

        Args:
            result:
                Final contract result.

            stake:
                Amount committed to the contract.

            payout:
                Net winning percentage.

        Returns:
            A tuple containing:

            - net profit;
            - returned amount.

        Raises:
            ValueError:
                If result is not a FixedTimeContractResult or is not a
                financially settleable result.
        """
        cls._validate_stake(stake)
        cls._validate_payout(payout)

        if not isinstance(
            result,
            FixedTimeContractResult,
        ):
            raise ValueError(
                "Result must be a FixedTimeContractResult instance."
            )

        if result is FixedTimeContractResult.WIN:
            net_profit = stake * payout
            returned_amount = stake + net_profit

            return net_profit, returned_amount

        if result is FixedTimeContractResult.LOSS:
            return -stake, cls._ZERO

        if result is FixedTimeContractResult.DRAW:
            return cls._ZERO, stake

        raise ValueError(
            "Financial settlement only accepts WIN, LOSS or DRAW."
        )

    @staticmethod
    def _validate_direction(
        direction: FixedTimeDirection,
    ) -> None:
        """Validate the fixed-time contract direction."""
        if not isinstance(
            direction,
            FixedTimeDirection,
        ):
            raise InvalidContractDirectionError(
                "Direction must be FixedTimeDirection.CALL "
                "or FixedTimeDirection.PUT."
            )

    @classmethod
    def _validate_stake(
        cls,
        stake: Decimal,
    ) -> None:
        """Validate a positive Decimal stake."""
        if not isinstance(stake, Decimal):
            raise InvalidStakeError(
                "Stake must use Decimal."
            )

        if not stake.is_finite():
            raise InvalidStakeError(
                "Stake must be a finite Decimal."
            )

        if stake <= cls._ZERO:
            raise InvalidStakeError(
                "Stake must be greater than zero."
            )

    @classmethod
    def _validate_payout(
        cls,
        payout: Decimal,
    ) -> None:
        """
        Validate the net payout percentage.

        Valid payout range:
            Greater than zero and less than or equal to one.
        """
        if not isinstance(payout, Decimal):
            raise InvalidPayoutError(
                "Payout must use Decimal."
            )

        if not payout.is_finite():
            raise InvalidPayoutError(
                "Payout must be a finite Decimal."
            )

        if payout <= cls._ZERO or payout > cls._ONE:
            raise InvalidPayoutError(
                "Payout must be greater than zero "
                "and less than or equal to one."
            )

    @classmethod
    def _validate_price(
        cls,
        price: Decimal,
        price_name: str,
    ) -> None:
        """Validate a positive and finite Decimal price."""
        if not isinstance(price, Decimal):
            raise InvalidContractPriceError(
                f"{price_name} must use Decimal."
            )

        if not price.is_finite():
            raise InvalidContractPriceError(
                f"{price_name} must be finite."
            )

        if price <= cls._ZERO:
            raise InvalidContractPriceError(
                f"{price_name} must be greater than zero."
            )