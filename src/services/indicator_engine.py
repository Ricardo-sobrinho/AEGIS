from src.market.event_data import CandlesReceivedEvent
from src.services.sma import SimpleMovingAverage


class IndicatorEngine:

    def __init__(self) -> None:
        self.sma = SimpleMovingAverage()

    def handle(
        self,
        event: CandlesReceivedEvent,
    ) -> None:

        sma = self.sma.calculate(event.candles)

        print()
        print("📈 Indicadores")
        print(f"SMA: {sma:.2f}")