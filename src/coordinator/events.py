"""
AEGIS - Trade Lifecycle Events

RFC-006

Define all events published by the TradeLifecycleCoordinator during the
complete lifecycle of a Fixed-Time Contract.

These events are consumed by the EventBus and allow complete decoupling
between application services.
"""

from __future__ import annotations

from enum import Enum


class TradeLifecycleEvent(str, Enum):
    """
    Official lifecycle events published by the TradeLifecycleCoordinator.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    TRADE_LIFECYCLE_STARTED = "trade.lifecycle.started"

    # ------------------------------------------------------------------
    # Risk
    # ------------------------------------------------------------------

    TRADE_RISK_APPROVED = "trade.risk.approved"

    TRADE_RISK_REJECTED = "trade.risk.rejected"

    # ------------------------------------------------------------------
    # Bankroll
    # ------------------------------------------------------------------

    TRADE_STAKE_RESERVED = "trade.stake.reserved"

    TRADE_STAKE_RELEASED = "trade.stake.released"

    # ------------------------------------------------------------------
    # Contract
    # ------------------------------------------------------------------

    TRADE_CREATED = "trade.created"

    TRADE_SUBMITTED = "trade.submitted"

    TRADE_ACCEPTED = "trade.accepted"

    TRADE_REJECTED = "trade.rejected"

    TRADE_ACTIVATED = "trade.activated"

    TRADE_EXPIRED = "trade.expired"

    # ------------------------------------------------------------------
    # Settlement
    # ------------------------------------------------------------------

    TRADE_SETTLED = "trade.settled"

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

    TRADE_COMPLETED = "trade.completed"

    TRADE_CANCELLED = "trade.cancelled"

    TRADE_FAILED = "trade.failed"