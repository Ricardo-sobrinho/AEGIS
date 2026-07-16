from dataclasses import dataclass

from src.models.signal import Signal


@dataclass
class StrategySignalEvent:
    symbol: str
    signal: Signal
    current_price: float