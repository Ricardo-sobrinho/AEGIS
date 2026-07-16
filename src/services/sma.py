from src.interfaces.indicator import Indicator
from src.models.candle import Candle


class SimpleMovingAverage(Indicator):

    def calculate(
        self,
        candles: list[Candle],
    ) -> float:

        if not candles:
            raise ValueError("Lista de candles vazia")

        total = sum(
            candle.close_price
            for candle in candles
        )

        return total / len(candles)