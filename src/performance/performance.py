from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Performance:
    """
    Immutable snapshot representing the portfolio performance at a
    specific point in time.
    """

    initial_equity: float

    equity: float

    realized_pnl: float

    unrealized_pnl: float

    total_pnl: float

    absolute_return: float

    return_percentage: float

    peak_equity: float

    drawdown: float

    drawdown_percentage: float

    maximum_drawdown: float

    maximum_drawdown_percentage: float