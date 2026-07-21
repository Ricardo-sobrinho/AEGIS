from dataclasses import dataclass

from src.models.candle import Candle


@dataclass(frozen=True, slots=True)
class CandlesReceivedEvent:
    symbol: str
    interval: str
    candles: list[Candle]


@dataclass(frozen=True, slots=True)
class PriceUpdatedEvent:
    symbol: str
    price: float