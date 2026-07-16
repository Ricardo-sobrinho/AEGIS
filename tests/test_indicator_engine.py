from src.market.event_data import CandlesReceivedEvent
from src.models.candle import Candle
from src.services.indicator_engine import IndicatorEngine


def create_candle(close_price: float) -> Candle:
    return Candle(
        open_time=0,
        open_price=0,
        high_price=0,
        low_price=0,
        close_price=close_price,
        volume=0,
    )


def test_indicator_engine_should_calculate_sma() -> None:
    engine = IndicatorEngine()

    candles = [
        create_candle(10),
        create_candle(20),
        create_candle(30),
    ]

    event = CandlesReceivedEvent(
        symbol="BTCUSDT",
        interval="1m",
        candles=candles,
    )

    engine.handle(event)