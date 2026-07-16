from dataclasses import dataclass


@dataclass
class RiskDecision:
    approved: bool
    reason: str