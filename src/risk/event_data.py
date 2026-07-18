from dataclasses import dataclass

from src.models.risk_decision import RiskDecision
from src.models.signal import Signal


@dataclass
class RiskDecisionEvent:
    symbol: str
    signal: Signal
    current_price: float
    decision: RiskDecision