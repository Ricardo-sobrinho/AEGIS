from dataclasses import dataclass


@dataclass
class Performance:
    equity: float
    unrealized_pnl: float
    roi: float