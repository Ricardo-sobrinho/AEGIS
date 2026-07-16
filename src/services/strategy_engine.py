from src.core.event_bus import EventBus
from src.market.event_data import CandlesReceivedEvent
from src.market.events import STRATEGY_SIGNAL_GENERATED
from src.market.strategy_event_data import StrategySignalEvent
from src.strategies.sma_strategy import SmaStrategy


class StrategyEngine:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.strategy = SmaStrategy()

    def handle(
        self,
        event: CandlesReceivedEvent,
    ) -> None:
        signal = self.strategy.evaluate(event)
        current_price = event.candles[-1].close_price

        print()
        print("🧠 Strategy Engine")
        print(f"Sinal gerado: {signal.value}")

        strategy_event = StrategySignalEvent(
            symbol=event.symbol,
            signal=signal,
            current_price=current_price,
        )

        self.event_bus.publish(
            STRATEGY_SIGNAL_GENERATED,
            strategy_event,
        )