from src.market.strategy_event_data import StrategySignalEvent
from src.models.risk_decision import RiskDecision
from src.models.signal import Signal


class RiskManager:
    def __init__(
        self,
        available_balance: float = 1000.0,
        minimum_balance: float = 100.0,
    ) -> None:
        self.available_balance = available_balance
        self.minimum_balance = minimum_balance

    def evaluate(
        self,
        event: StrategySignalEvent,
    ) -> RiskDecision:
        if event.signal == Signal.HOLD:
            return RiskDecision(
                approved=False,
                reason="Sinal HOLD não gera operação",
            )

        if self.available_balance < self.minimum_balance:
            return RiskDecision(
                approved=False,
                reason="Saldo abaixo do mínimo permitido",
            )

        return RiskDecision(
            approved=True,
            reason="Operação dentro dos limites definidos",
        )

    def handle(
        self,
        event: StrategySignalEvent,
    ) -> None:
        decision = self.evaluate(event)

        print()
        print("🛡️ Risk Manager")
        print(f"Aprovado: {decision.approved}")
        print(f"Motivo: {decision.reason}")