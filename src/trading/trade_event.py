from dataclasses import dataclass

from src.models.signal import Signal


@dataclass
class TradeEvent:
    symbol: str
    signal: Signal
    price: float
    quantity: float