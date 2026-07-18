from src.core.event_bus import EventBus
from src.execution.events import TRADE_REQUESTED
from src.risk.event_data import RiskDecisionEvent
from src.trading.trade_event import TradeEvent


class ExecutionEngine:
    def __init__(
        self,
        event_bus: EventBus,
        mode: str = "paper",
        default_quantity: float = 1.0,
    ) -> None:
        self.event_bus = event_bus
        self.mode = mode
        self.default_quantity = default_quantity

    def handle(
        self,
        event: RiskDecisionEvent,
    ) -> None:
        if not event.decision.approved:
            return

        trade = TradeEvent(
            symbol=event.symbol,
            signal=event.signal,
            price=event.current_price,
            quantity=self.default_quantity,
        )

        self._show_trade_request(trade)

        self.event_bus.publish(
            TRADE_REQUESTED,
            trade,
        )

    def _show_trade_request(
        self,
        trade: TradeEvent,
    ) -> None:
        print()
        print("⚙️ Execution Engine")
        print("----------------------------")
        print(f"Modo............: {self.mode.upper()}")
        print(f"Ativo...........: {trade.symbol}")
        print(f"Operação........: {trade.signal.value}")
        print(f"Preço...........: {trade.price:.2f}")
        print(f"Quantidade......: {trade.quantity}")
        print("Status..........: ordem solicitada")