from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    quantity: float
    average_price: float
    last_price: float

    @property
    def invested_value(self) -> float:
        return self.quantity * self.average_price

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.invested_value

    @property
    def return_percentage(self) -> float:
        if self.average_price <= 0:
            return 0.0

        return (
            (self.last_price - self.average_price)
            / self.average_price
        ) * 100


@dataclass
class Portfolio:
    cash: float = 10000.0
    positions: dict[str, Position] = field(
        default_factory=dict
    )
    realized_pnl: float = 0.0

    @property
    def invested_value(self) -> float:
        return sum(
            position.invested_value
            for position in self.positions.values()
        )

    @property
    def market_value(self) -> float:
        return sum(
            position.market_value
            for position in self.positions.values()
        )

    @property
    def unrealized_pnl(self) -> float:
        return sum(
            position.unrealized_pnl
            for position in self.positions.values()
        )

    @property
    def equity(self) -> float:
        return self.cash + self.market_value