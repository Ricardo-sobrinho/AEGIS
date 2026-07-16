from src.market.strategy_event_data import StrategySignalEvent
from src.models.signal import Signal
from src.services.risk_manager import RiskManager


def create_event(signal: Signal) -> StrategySignalEvent:
    return StrategySignalEvent(
        symbol="BTCUSDT",
        signal=signal,
        current_price=65000.0,
    )


def test_buy_signal_should_be_approved_with_sufficient_balance() -> None:
    risk_manager = RiskManager(
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
        available_balance=1000.0,
        minimum_balance=100.0,
    )

    decision = risk_manager.evaluate(
        create_event(Signal.SELL)
    )

    assert decision.approved is True


def test_hold_signal_should_be_blocked() -> None:
    risk_manager = RiskManager()

    decision = risk_manager.evaluate(
        create_event(Signal.HOLD)
    )

    assert decision.approved is False
    assert decision.reason == "Sinal HOLD não gera operação"


def test_signal_should_be_blocked_when_balance_is_too_low() -> None:
    risk_manager = RiskManager(
        available_balance=50.0,
        minimum_balance=100.0,
    )

    decision = risk_manager.evaluate(
        create_event(Signal.BUY)
    )

    assert decision.approved is False
    assert decision.reason == "Saldo abaixo do mínimo permitido"