from src.core.event_bus import EventBus


def test_publish_should_call_subscribed_handler() -> None:
    event_bus = EventBus()
    received_events: list[str] = []

    def handler(message: str) -> None:
        received_events.append(message)

    event_bus.subscribe(
        event_name="system.started",
        handler=handler,
    )

    event_bus.publish(
        event_name="system.started",
        event_data="AEGIS iniciada",
    )

    assert received_events == ["AEGIS iniciada"]


def test_publish_should_call_multiple_handlers() -> None:
    event_bus = EventBus()
    results: list[str] = []

    def first_handler(message: str) -> None:
        results.append(f"primeiro: {message}")

    def second_handler(message: str) -> None:
        results.append(f"segundo: {message}")

    event_bus.subscribe("market.updated", first_handler)
    event_bus.subscribe("market.updated", second_handler)

    event_bus.publish("market.updated", "BTCUSDT")

    assert results == [
        "primeiro: BTCUSDT",
        "segundo: BTCUSDT",
    ]


def test_unsubscribe_should_remove_handler() -> None:
    event_bus = EventBus()
    received_events: list[str] = []

    def handler(message: str) -> None:
        received_events.append(message)

    event_bus.subscribe("system.stopped", handler)
    event_bus.unsubscribe("system.stopped", handler)

    event_bus.publish("system.stopped", "AEGIS encerrada")

    assert received_events == []