from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    quantity: float
    average_price: float


@dataclass
class Portfolio:

    cash: float = 10000.0

    positions: dict[str, Position] = field(
        default_factory=dict
    )