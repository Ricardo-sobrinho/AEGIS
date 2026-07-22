"""
AEGIS - Trade Event Handler

RFC-006

Defines the standard contract implemented by every event-driven
Trade Lifecycle handler.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.coordinator.handlers.base_handler import BaseHandler


class TradeEventHandler(BaseHandler, ABC):
    """
    Base abstraction for Trade Lifecycle event handlers.

    Every concrete handler must declare which events it listens to
    and how its subscriptions are registered in the EventBus.
    """

    @property
    @abstractmethod
    def subscribed_events(self) -> tuple[str, ...]:
        """
        Returns the names of the events handled by this component.
        """
        raise NotImplementedError

    @abstractmethod
    def register(self) -> None:
        """
        Registers the handler subscriptions in the EventBus.
        """
        raise NotImplementedError