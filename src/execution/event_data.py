from dataclasses import dataclass

from src.trading.trade_event import TradeEvent


@dataclass
class TradeRejectedEvent:
    trade: TradeEvent
    reason: str