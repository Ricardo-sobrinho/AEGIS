from src.core.event_bus import EventBus
from src.market.strategy_event_data import StrategySignalEvent
from src.models.risk_decision import RiskDecision
from src.models.signal import Signal
from src.portfolio.event_data import PortfolioUpdatedEvent
from src.risk.event_data import RiskDecisionEvent
from src.risk.events import (
    RISK_OPERATION_APPROVED,
    RISK_OPERATION_BLOCKED,
)
from src.trading.trade_event import TradeEvent


class RiskManager:
    def __init__(
        self,
        event_bus: EventBus,
        available_balance: float = 1000.0,
        minimum_balance: float = 100.0,
    ) -> None:
        self.event_bus = event_bus
        self.available_balance = available_balance
        self.minimum_balance = minimum_balance

        self.open_positions: set[str] = set()

        self.last_executed_signals: dict[
            str,
            Signal,
        ] = {}

    def handle_portfolio_update(
        self,
        event: PortfolioUpdatedEvent,
    ) -> None:
        self.available_balance = event.portfolio.cash

        self.open_positions = set(
            event.portfolio.positions.keys()
        )

    def handle_trade_executed(
        self,
        trade: TradeEvent,
    ) -> None:
        self.last_executed_signals[
            trade.symbol
        ] = trade.signal

        print()
        print("✅ Risk State Updated")
        print("----------------------------")
        print(f"Ativo...........: {trade.symbol}")
        print(f"Última execução.: {trade.signal.value}")

    def evaluate(
        self,
        event: StrategySignalEvent,
    ) -> RiskDecision:
        if event.signal == Signal.HOLD:
            return RiskDecision(
                approved=False,
                reason="Sinal HOLD não gera operação",
            )

        if event.signal == Signal.BUY:
            return self._evaluate_buy(event)

        if event.signal == Signal.SELL:
            return self._evaluate_sell(event)

        return RiskDecision(
            approved=False,
            reason="Sinal de operação desconhecido",
        )

    def _evaluate_buy(
        self,
        event: StrategySignalEvent,
    ) -> RiskDecision:
        if event.symbol in self.open_positions:
            return RiskDecision(
                approved=False,
                reason=(
                    "Já existe uma posição aberta "
                    "para este ativo"
                ),
            )

        last_signal = self.last_executed_signals.get(
            event.symbol
        )

        if last_signal == Signal.BUY:
            return RiskDecision(
                approved=False,
                reason=(
                    "Sinal BUY repetido sem uma venda "
                    "executada entre as operações"
                ),
            )

        if self.available_balance < self.minimum_balance:
            return RiskDecision(
                approved=False,
                reason="Saldo abaixo do mínimo permitido",
            )

        if event.current_price <= 0:
            return RiskDecision(
                approved=False,
                reason="Preço de compra inválido",
            )

        return RiskDecision(
            approved=True,
            reason="Operação de compra dentro dos limites",
        )

    def _evaluate_sell(
        self,
        event: StrategySignalEvent,
    ) -> RiskDecision:
        if event.symbol not in self.open_positions:
            return RiskDecision(
                approved=False,
                reason=(
                    "Não existe posição aberta "
                    "para realizar a venda"
                ),
            )

        last_signal = self.last_executed_signals.get(
            event.symbol
        )

        if last_signal == Signal.SELL:
            return RiskDecision(
                approved=False,
                reason=(
                    "Sinal SELL repetido sem uma compra "
                    "executada entre as operações"
                ),
            )

        if event.current_price <= 0:
            return RiskDecision(
                approved=False,
                reason="Preço de venda inválido",
            )

        return RiskDecision(
            approved=True,
            reason="Operação de venda dentro dos limites",
        )

    def handle(
        self,
        event: StrategySignalEvent,
    ) -> None:
        decision = self.evaluate(event)

        risk_event = RiskDecisionEvent(
            symbol=event.symbol,
            signal=event.signal,
            current_price=event.current_price,
            decision=decision,
        )

        print()
        print("🛡️ Risk Manager")
        print("----------------------------")
        print(f"Ativo...........: {event.symbol}")
        print(f"Sinal...........: {event.signal.value}")
        print(f"Aprovado........: {decision.approved}")
        print(f"Motivo..........: {decision.reason}")

        if decision.approved:
            self.event_bus.publish(
                RISK_OPERATION_APPROVED,
                risk_event,
            )
            return

        self.event_bus.publish(
            RISK_OPERATION_BLOCKED,
            risk_event,
        )