"""
AEGIS - Trade Lifecycle Coordinator Tests

RFC-006

Tests the infrastructure and lifecycle behavior of the
TradeLifecycleCoordinator.
"""

from __future__ import annotations

import unittest

from src.coordinator.handlers.trade_event_handler import TradeEventHandler
from src.coordinator.trade_lifecycle_coordinator import (
    TradeLifecycleCoordinator,
)
from src.core.event_bus import EventBus


class FakeTradeEventHandler(TradeEventHandler):
    """
    Test double used to verify coordinator behavior.
    """

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)
        self.register_calls = 0

    @property
    def subscribed_events(self) -> tuple[str, ...]:
        """
        Returns the event names handled by this test double.
        """
        return ("fake_trade_event",)

    def register(self) -> None:
        """
        Records how many times registration was requested.
        """
        self.register_calls += 1


class TradeLifecycleCoordinatorTestCase(unittest.TestCase):
    """
    Tests for TradeLifecycleCoordinator.
    """

    def setUp(self) -> None:
        self.event_bus = EventBus()
        self.handler = FakeTradeEventHandler(self.event_bus)

        self.coordinator = TradeLifecycleCoordinator(
            event_bus=self.event_bus,
            handlers=(self.handler,),
        )

    def test_coordinator_starts_as_not_started(self) -> None:
        self.assertFalse(self.coordinator.started)

    def test_start_marks_coordinator_as_started(self) -> None:
        self.coordinator.start()

        self.assertTrue(self.coordinator.started)

    def test_start_registers_handlers(self) -> None:
        self.coordinator.start()

        self.assertEqual(self.handler.register_calls, 1)

    def test_repeated_start_does_not_register_handlers_twice(self) -> None:
        self.coordinator.start()
        self.coordinator.start()

        self.assertEqual(self.handler.register_calls, 1)

    def test_stop_marks_coordinator_as_not_started(self) -> None:
        self.coordinator.start()
        self.coordinator.stop()

        self.assertFalse(self.coordinator.started)

    def test_restart_does_not_duplicate_handler_registration(self) -> None:
        self.coordinator.start()
        self.coordinator.stop()
        self.coordinator.start()

        self.assertTrue(self.coordinator.started)
        self.assertEqual(self.handler.register_calls, 1)

    def test_event_bus_is_exposed(self) -> None:
        self.assertIs(self.coordinator.event_bus, self.event_bus)

    def test_handlers_are_exposed_as_tuple(self) -> None:
        self.assertEqual(
            self.coordinator.handlers,
            (self.handler,),
        )


if __name__ == "__main__":
    unittest.main()