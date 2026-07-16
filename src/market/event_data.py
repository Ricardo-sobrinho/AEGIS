from dataclasses import dataclass

from src.models.candle import Candle


@dataclass
class CandlesReceivedEvent:
    symbol: str
    interval: str
    candles: list[Candle]