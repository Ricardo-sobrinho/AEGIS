"""
AEGIS - Fixed-Time Contract Settlement

Define as regras de determinação de resultado e cálculo financeiro
dos contratos de tempo fixo.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.fixed_time.enums import (
    ContractResult,
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
    Representa o resultado financeiro calculado para um contrato.
    """

    result: ContractResult
    net_profit: Decimal
    returned_amount: Decimal


class FixedTimeSettlementCalculator:
    """
    Calcula o resultado operacional e financeiro de um contrato
    de tempo fixo.
    """

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
        Determina o resultado e calcula seus valores financeiros.

        Args:
            direction:
                Direção CALL ou PUT do contrato.
            stake:
                Valor comprometido na operação.
            payout:
                Percentual líquido de lucro em caso de vitória.
                Exemplo: Decimal("0.80") representa 80%.
            entry_price:
                Preço do ativo no início do contrato.
            expiration_price:
                Preço do ativo no encerramento do contrato.

        Returns:
            Um objeto SettlementCalculation contendo resultado,
            lucro líquido e valor devolvido.

        Raises:
            InvalidContractDirectionError:
                Quando a direção não é válida.
            InvalidStakeError:
                Quando a stake não utiliza Decimal ou não é positiva.
            InvalidPayoutError:
                Quando o payout não utiliza Decimal ou está fora
                do intervalo permitido.
            InvalidContractPriceError:
                Quando algum preço é inválido.
        """

        cls._validate_direction(direction)
        cls._validate_stake(stake)
        cls._validate_payout(payout)
        cls._validate_price(entry_price, "O preço de entrada")
        cls._validate_price(
            expiration_price,
            "O preço de expiração",
        )

        result = cls.determine_result(
            direction=direction,
            entry_price=entry_price,
            expiration_price=expiration_price,
        )

        net_profit, returned_amount = cls.calculate_financial_result(
            result=result,
            stake=stake,
            payout=payout,
        )

        return SettlementCalculation(
            result=result,
            net_profit=net_profit,
            returned_amount=returned_amount,
        )

    @staticmethod
    def determine_result(
        direction: FixedTimeDirection,
        entry_price: Decimal,
        expiration_price: Decimal,
    ) -> ContractResult:
        """
        Determina se o contrato terminou em WIN, LOSS ou DRAW.
        """

        FixedTimeSettlementCalculator._validate_direction(direction)
        FixedTimeSettlementCalculator._validate_price(
            entry_price,
            "O preço de entrada",
        )
        FixedTimeSettlementCalculator._validate_price(
            expiration_price,
            "O preço de expiração",
        )

        if expiration_price == entry_price:
            return ContractResult.DRAW

        if direction == FixedTimeDirection.CALL:
            if expiration_price > entry_price:
                return ContractResult.WIN

            return ContractResult.LOSS

        if expiration_price < entry_price:
            return ContractResult.WIN

        return ContractResult.LOSS

    @staticmethod
    def calculate_financial_result(
        result: ContractResult,
        stake: Decimal,
        payout: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """
        Calcula o lucro líquido e o valor devolvido ao saldo.
        """

        FixedTimeSettlementCalculator._validate_stake(stake)
        FixedTimeSettlementCalculator._validate_payout(payout)

        if not isinstance(result, ContractResult):
            raise ValueError(
                "O resultado deve ser uma instância de ContractResult."
            )

        if result == ContractResult.WIN:
            net_profit = stake * payout
            returned_amount = stake + net_profit

            return net_profit, returned_amount

        if result == ContractResult.LOSS:
            return -stake, Decimal("0")

        return Decimal("0"), stake

    @staticmethod
    def _validate_direction(
        direction: FixedTimeDirection,
    ) -> None:
        """
        Valida a direção do contrato.
        """

        if not isinstance(direction, FixedTimeDirection):
            raise InvalidContractDirectionError(
                "A direção deve ser FixedTimeDirection.CALL "
                "ou FixedTimeDirection.PUT."
            )

    @staticmethod
    def _validate_stake(stake: Decimal) -> None:
        """
        Valida a stake do contrato.
        """

        if not isinstance(stake, Decimal):
            raise InvalidStakeError(
                "A stake deve utilizar Decimal."
            )

        if stake <= Decimal("0"):
            raise InvalidStakeError(
                "A stake deve ser maior que zero."
            )

    @staticmethod
    def _validate_payout(payout: Decimal) -> None:
        """
        Valida o payout líquido.
        """

        if not isinstance(payout, Decimal):
            raise InvalidPayoutError(
                "O payout deve utilizar Decimal."
            )

        if payout < Decimal("0") or payout > Decimal("1"):
            raise InvalidPayoutError(
                "O payout deve estar entre 0 e 1."
            )

    @staticmethod
    def _validate_price(
        price: Decimal,
        price_name: str,
    ) -> None:
        """
        Valida um preço financeiro.
        """

        if not isinstance(price, Decimal):
            raise InvalidContractPriceError(
                f"{price_name} deve utilizar Decimal."
            )

        if price <= Decimal("0"):
            raise InvalidContractPriceError(
                f"{price_name} deve ser maior que zero."
            )