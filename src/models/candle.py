from dataclasses import dataclass


@dataclass
class Candle:
    open_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float