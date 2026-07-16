from abc import ABC, abstractmethod

from src.models.candle import Candle


class Indicator(ABC):

    @abstractmethod
    def calculate(
        self,
        candles: list[Candle],
    ) -> float:
        pass