from src.execution.events import (
    TRADE_EXECUTED,
    TRADE_REJECTED,
    TRADE_REQUESTED,
)

TRADE_OPENED = TRADE_EXECUTED
TRADE_CLOSED = "trade.closed"

__all__ = [
    "TRADE_REQUESTED",
    "TRADE_EXECUTED",
    "TRADE_REJECTED",
    "TRADE_OPENED",
    "TRADE_CLOSED",
]