"""
AEGIS - Risk Handler

RFC-006

Coordinates the risk evaluation stage of the Trade Lifecycle.
"""

from __future__ import annotations

from src.coordinator.events import TradeLifecycleEvent
from src.coordinator.handlers.trade_event_handler import TradeEventHandler
from src.core.event_bus import EventBus
from src.services.risk_manager import RiskManager


class RiskHandler(TradeEventHandler):
    """
    Handles the risk evaluation stage of the trade lifecycle.
    """

    def __init__(
        self,
        event_bus: EventBus,
        risk_manager: RiskManager,
    ) -> None:
        super().__init__(event_bus)
        self._risk_manager = risk_manager

    @property
    def subscribed_events(self) -> tuple[str, ...]:
        """
        Returns the event names handled by this component.
        """
        return (
            TradeLifecycleEvent.TRADE_LIFECYCLE_STARTED.value,
        )

    def register(self) -> None:
        """
        Registers this handler in the EventBus.
        """
        for event_name in self.subscribed_events:
            self.event_bus.subscribe(event_name, self.handle)

    def handle(self, event_data: object) -> None:
        """
        Handles a Trade Lifecycle event.

        Business orchestration will be implemented in a later phase.
        """
        raise NotImplementedError(
            "RiskHandler.handle() not implemented yet."
        )