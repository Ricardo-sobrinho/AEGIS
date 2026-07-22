"""
AEGIS - Trade Lifecycle Coordinator

RFC-006

Application service responsible for orchestrating the lifecycle of
Fixed-Time Contracts.

Current implementation:
- Handler dependency registration
- Handler subscription initialization
- Idempotent coordinator startup
- Coordinator lifecycle control

Business rules remain inside the domain components and handlers.
"""

from __future__ import annotations

from collections.abc import Iterable

from src.coordinator.handlers.trade_event_handler import TradeEventHandler
from src.core.event_bus import EventBus


class TradeLifecycleCoordinator:
    """
    Application service responsible for initializing and coordinating
    the event-driven Trade Lifecycle workflow.

    The coordinator does not contain business rules. Each lifecycle
    stage is handled by a specialized TradeEventHandler.
    """

    def __init__(
        self,
        event_bus: EventBus,
        handlers: Iterable[TradeEventHandler] | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._handlers = tuple(handlers or ())
        self._started = False
        self._handlers_registered = False

    @property
    def event_bus(self) -> EventBus:
        """
        Returns the EventBus used by the coordinator.
        """
        return self._event_bus

    @property
    def handlers(self) -> tuple[TradeEventHandler, ...]:
        """
        Returns the registered Trade Lifecycle handlers.
        """
        return self._handlers

    @property
    def started(self) -> bool:
        """
        Returns whether the coordinator has been started.
        """
        return self._started

    def start(self) -> None:
        """
        Starts the coordinator and registers its handlers.

        Repeated calls do not create duplicated EventBus subscriptions.
        """
        if self._started:
            return

        if not self._handlers_registered:
            self._register_handlers()
            self._handlers_registered = True

        self._started = True

    def stop(self) -> None:
        """
        Marks the coordinator as stopped.

        EventBus unsubscription will be implemented when the handler
        lifecycle contract receives unregister support.
        """
        self._started = False

    def _register_handlers(self) -> None:
        """
        Registers every Trade Lifecycle handler in the EventBus.
        """
        for handler in self._handlers:
            handler.register()