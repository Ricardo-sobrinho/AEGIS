from abc import ABC, abstractmethod

from src.market.event_data import CandlesReceivedEvent
from src.models.signal import Signal


class Strategy(ABC):

    @abstractmethod
    def evaluate(
        self,
        event: CandlesReceivedEvent,
    ) -> Signal:
        pass