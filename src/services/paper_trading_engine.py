from src.core.event_bus import EventBus
from src.models.signal import Signal
from src.risk.event_data import RiskDecisionEvent
from src.risk.events import RISK_OPERATION_APPROVED
from src.trading.events import TRADE_OPENED
from src.trading.trade_event import TradeEvent


class PaperTradingEngine:

    def __init__(
        self,
        event_bus: EventBus,
    ) -> None:
        self.event_bus = event_bus

    def handle(
        self,
        event: RiskDecisionEvent,
    ) -> None:

        quantity = 1.0

        trade = TradeEvent(
            symbol=event.symbol,
            signal=event.signal,
            price=event.current_price,
            quantity=quantity,
        )

        self.event_bus.publish(
            TRADE_OPENED,
            trade,
        )

        print()
        print("📄 Paper Trading")
        print(f"Ativo: {trade.symbol}")
        print(f"Sinal: {trade.signal.value}")
        print(f"Preço: {trade.price:.2f}")
        print(f"Quantidade: {trade.quantity}")