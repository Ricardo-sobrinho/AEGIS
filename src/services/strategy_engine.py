from typing import Any

from src.core.event_bus import EventBus
from src.market.event_data import CandlesReceivedEvent
from src.market.events import STRATEGY_SIGNAL_GENERATED
from src.market.strategy_event_data import StrategySignalEvent
from src.models.signal import Signal
from src.strategies.sma_strategy import SmaStrategy


class StrategyEngine:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.strategy = SmaStrategy()

        self.last_processed_candles: dict[str, str] = {}
        self.last_generated_signals: dict[str, Signal] = {}

    def handle(
        self,
        event: CandlesReceivedEvent,
    ) -> None:
        if not event.candles:
            print()
            print("⚠️ Strategy Engine")
            print("Nenhum candle disponível para análise.")
            return

        latest_candle = event.candles[-1]

        candle_identifier = self._get_candle_identifier(
            symbol=event.symbol,
            interval=event.interval,
            candle=latest_candle,
        )

        market_key = self._get_market_key(
            symbol=event.symbol,
            interval=event.interval,
        )

        last_candle_identifier = (
            self.last_processed_candles.get(market_key)
        )

        if last_candle_identifier == candle_identifier:
            print()
            print("🧠 Strategy Engine")
            print(
                "Candle ignorado: este candle já foi processado."
            )
            return

        self.last_processed_candles[
            market_key
        ] = candle_identifier

        signal = self.strategy.evaluate(event)
        current_price = float(latest_candle.close_price)

        previous_signal = self.last_generated_signals.get(
            event.symbol
        )

        self.last_generated_signals[event.symbol] = signal

        print()
        print("🧠 Strategy Engine")
        print(f"Sinal gerado: {signal.value}")

        if previous_signal is not None:
            print(f"Sinal anterior: {previous_signal.value}")

        strategy_event = StrategySignalEvent(
            symbol=event.symbol,
            signal=signal,
            current_price=current_price,
        )

        self.event_bus.publish(
            STRATEGY_SIGNAL_GENERATED,
            strategy_event,
        )

    def _get_market_key(
        self,
        symbol: str,
        interval: str,
    ) -> str:
        return f"{symbol}:{interval}"

    def _get_candle_identifier(
        self,
        symbol: str,
        interval: str,
        candle: Any,
    ) -> str:
        possible_time_attributes = (
            "open_time",
            "close_time",
            "timestamp",
            "time",
            "open_timestamp",
            "close_timestamp",
        )

        for attribute_name in possible_time_attributes:
            attribute_value = getattr(
                candle,
                attribute_name,
                None,
            )

            if attribute_value is not None:
                return (
                    f"{symbol}:"
                    f"{interval}:"
                    f"{attribute_name}:"
                    f"{attribute_value}"
                )

        return (
            f"{symbol}:"
            f"{interval}:"
            f"{repr(candle)}"
        )