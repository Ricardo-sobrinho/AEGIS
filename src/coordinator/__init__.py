"""
AEGIS - Trade Lifecycle Coordinator Package

RFC-006

Application-layer package responsible for orchestrating the complete
lifecycle of Fixed-Time Contract operations.

The package coordinates domain services and infrastructure abstractions
without assuming responsibilities that belong to Risk, Bankroll,
Fixed-Time, Execution, Settlement or Performance components.
"""

from __future__ import annotations

from src.coordinator.events import TradeLifecycleEvent
from src.coordinator.exceptions import (
    TradeLifecycleActivationError,
    TradeLifecycleAlreadyCompletedError,
    TradeLifecycleAlreadyStartedError,
    TradeLifecycleContractCreationError,
    TradeLifecycleCoordinatorError,
    TradeLifecycleDependencyError,
    TradeLifecycleExecutionRejectedError,
    TradeLifecycleExpirationError,
    TradeLifecycleNotStartedError,
    TradeLifecyclePerformanceUpdateError,
    TradeLifecycleRiskRejectedError,
    TradeLifecycleRollbackError,
    TradeLifecycleSettlementError,
    TradeLifecycleStakeReservationError,
    TradeLifecycleSubmissionError,
)

__all__ = [
    "TradeLifecycleActivationError",
    "TradeLifecycleAlreadyCompletedError",
    "TradeLifecycleAlreadyStartedError",
    "TradeLifecycleContractCreationError",
    "TradeLifecycleCoordinatorError",
    "TradeLifecycleDependencyError",
    "TradeLifecycleEvent",
    "TradeLifecycleExecutionRejectedError",
    "TradeLifecycleExpirationError",
    "TradeLifecycleNotStartedError",
    "TradeLifecyclePerformanceUpdateError",
    "TradeLifecycleRiskRejectedError",
    "TradeLifecycleRollbackError",
    "TradeLifecycleSettlementError",
    "TradeLifecycleStakeReservationError",
    "TradeLifecycleSubmissionError",
]