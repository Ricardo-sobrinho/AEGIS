from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        self._subscribers[event_name].append(handler)

    def publish(
        self,
        event_name: str,
        event_data: Any,
    ) -> None:
        handlers = self._subscribers.get(event_name, [])

        for handler in handlers:
            handler(event_data)

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        handlers = self._subscribers.get(event_name, [])

        if handler in handlers:
            handlers.remove(handler)