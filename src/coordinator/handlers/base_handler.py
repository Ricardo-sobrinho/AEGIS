"""
AEGIS - Base Handler

RFC-006

Base infrastructure shared by every Trade Lifecycle handler.
"""

from __future__ import annotations

from abc import ABC

from src.core.event_bus import EventBus


class BaseHandler(ABC):
    """
    Base class for all Trade Lifecycle handlers.

    Provides common infrastructure and utility methods shared by
    every handler implementation.
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    @property
    def event_bus(self) -> EventBus:
        """
        Returns the EventBus instance.
        """
        return self._event_bus

    def publish(self, event_name: str, event_data: object) -> None:
        """
        Publishes an event through the EventBus.
        """
        self._event_bus.publish(event_name, event_data)