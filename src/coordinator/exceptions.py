"""
AEGIS - Trade Lifecycle Coordinator Exceptions

RFC-006

Defines the exception hierarchy used by the TradeLifecycleCoordinator.

These exceptions belong to the application orchestration layer and must not
replace domain-specific exceptions raised by Risk, Bankroll, Fixed-Time,
Execution or Performance components.
"""

from __future__ import annotations


class TradeLifecycleCoordinatorError(Exception):
    """
    Base exception for all TradeLifecycleCoordinator errors.
    """


class TradeLifecycleAlreadyStartedError(TradeLifecycleCoordinatorError):
    """
    Raised when an attempt is made to start an already-started lifecycle.
    """


class TradeLifecycleNotStartedError(TradeLifecycleCoordinatorError):
    """
    Raised when an operation requires a lifecycle that has not been started.
    """


class TradeLifecycleAlreadyCompletedError(TradeLifecycleCoordinatorError):
    """
    Raised when an operation is attempted after lifecycle completion.
    """


class TradeLifecycleRiskRejectedError(TradeLifecycleCoordinatorError):
    """
    Raised when the RiskManager rejects a trade intent.
    """


class TradeLifecycleStakeReservationError(TradeLifecycleCoordinatorError):
    """
    Raised when the coordinator cannot reserve the required stake.
    """


class TradeLifecycleContractCreationError(TradeLifecycleCoordinatorError):
    """
    Raised when a Fixed-Time Contract cannot be created.
    """


class TradeLifecycleSubmissionError(TradeLifecycleCoordinatorError):
    """
    Raised when a contract cannot be submitted for execution.
    """


class TradeLifecycleExecutionRejectedError(TradeLifecycleCoordinatorError):
    """
    Raised when the execution provider rejects the submitted contract.
    """


class TradeLifecycleActivationError(TradeLifecycleCoordinatorError):
    """
    Raised when an accepted contract cannot be activated.
    """


class TradeLifecycleExpirationError(TradeLifecycleCoordinatorError):
    """
    Raised when the contract expiration stage cannot be completed.
    """


class TradeLifecycleSettlementError(TradeLifecycleCoordinatorError):
    """
    Raised when result calculation or financial settlement fails.
    """


class TradeLifecyclePerformanceUpdateError(TradeLifecycleCoordinatorError):
    """
    Raised when the PerformanceEngine cannot process the completed trade.
    """


class TradeLifecycleRollbackError(TradeLifecycleCoordinatorError):
    """
    Raised when compensation or rollback of a partially completed flow fails.
    """


class TradeLifecycleDependencyError(TradeLifecycleCoordinatorError):
    """
    Raised when a required coordinator dependency is missing or invalid.
    """