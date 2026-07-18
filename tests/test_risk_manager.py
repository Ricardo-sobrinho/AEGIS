from src.core.event_bus import EventBus
from src.market.strategy_event_data import StrategySignalEvent
from src.models.signal import Signal
from src.risk.event_data import RiskDecisionEvent
from src.risk.events import (
    RISK_OPERATION_APPROVED,
    RISK_OPERATION_BLOCKED,
)
from src.services.risk_manager import RiskManager


def create_event(signal: Signal) -> StrategySignalEvent:
    return StrategySignalEvent(
        symbol="BTCUSDT",
        signal=signal,
        current_price=65000.0,
    )


def test_buy_signal_should_be_approved_with_sufficient_balance() -> None:
    risk_manager = RiskManager(
        event_bus=EventBus(),
        available_balance=1000.0,
        minimum_balance=100.0,
    )

    decision = risk_manager.evaluate(
        create_event(Signal.BUY)
    )

    assert decision.approved is True
    assert decision.reason == "Operação dentro dos limites definidos"


def test_sell_signal_should_be_approved_with_sufficient_balance() -> None:
    risk_manager = RiskManager(
        event_bus=EventBus(),
        available_balance=1000.0,
        minimum_balance=100.0,
    )

    decision = risk_manager.evaluate(
        create_event(Signal.SELL)
    )

    assert decision.approved is True
    assert decision.reason == "Operação dentro dos limites definidos"


def test_hold_signal_should_be_blocked() -> None:
    risk_manager = RiskManager(
        event_bus=EventBus()
    )

    decision = risk_manager.evaluate(
        create_event(Signal.HOLD)
    )

    assert decision.approved is False
    assert decision.reason == "Sinal HOLD não gera operação"


def test_signal_should_be_blocked_when_balance_is_too_low() -> None:
    risk_manager = RiskManager(
        event_bus=EventBus(),
        available_balance=50.0,
        minimum_balance=100.0,
    )

    decision = risk_manager.evaluate(
        create_event(Signal.BUY)
    )

    assert decision.approved is False
    assert decision.reason == "Saldo abaixo do mínimo permitido"


def test_handle_should_publish_approved_event() -> None:
    event_bus = EventBus()
    received_events: list[RiskDecisionEvent] = []

    event_bus.subscribe(
        RISK_OPERATION_APPROVED,
        received_events.append,
    )

    risk_manager = RiskManager(
        event_bus=event_bus,
        available_balance=1000.0,
        minimum_balance=100.0,
    )

    risk_manager.handle(
        create_event(Signal.BUY)
    )

    assert len(received_events) == 1
    assert received_events[0].decision.approved is True
    assert received_events[0].signal == Signal.BUY
    assert received_events[0].symbol == "BTCUSDT"
    assert received_events[0].current_price == 65000.0


def test_handle_should_publish_blocked_event_for_low_balance() -> None:
    event_bus = EventBus()
    received_events: list[RiskDecisionEvent] = []

    event_bus.subscribe(
        RISK_OPERATION_BLOCKED,
        received_events.append,
    )

    risk_manager = RiskManager(
        event_bus=event_bus,
        available_balance=50.0,
        minimum_balance=100.0,
    )

    risk_manager.handle(
        create_event(Signal.BUY)
    )

    assert len(received_events) == 1
    assert received_events[0].decision.approved is False
    assert received_events[0].decision.reason == (
        "Saldo abaixo do mínimo permitido"
    )
    assert received_events[0].signal == Signal.BUY


def test_handle_should_publish_blocked_event_for_hold_signal() -> None:
    event_bus = EventBus()
    received_events: list[RiskDecisionEvent] = []

    event_bus.subscribe(
        RISK_OPERATION_BLOCKED,
        received_events.append,
    )

    risk_manager = RiskManager(
        event_bus=event_bus,
        available_balance=1000.0,
        minimum_balance=100.0,
    )

    risk_manager.handle(
        create_event(Signal.HOLD)
    )

    assert len(received_events) == 1
    assert received_events[0].decision.approved is False
    assert received_events[0].decision.reason == (
        "Sinal HOLD não gera operação"
    )
    assert received_events[0].signal == Signal.HOLD