from src.interfaces.strategy import Strategy
from src.market.event_data import CandlesReceivedEvent
from src.models.signal import Signal
from src.services.sma import SimpleMovingAverage


class SmaStrategy(Strategy):

    def __init__(self) -> None:
        self.sma = SimpleMovingAverage()

    def evaluate(
        self,
        event: CandlesReceivedEvent,
    ) -> Signal:

        sma = self.sma.calculate(event.candles)

        last_price = event.candles[-1].close_price

        if last_price > sma:
            return Signal.BUY

        if last_price < sma:
            return Signal.SELL

        return Signal.HOLD