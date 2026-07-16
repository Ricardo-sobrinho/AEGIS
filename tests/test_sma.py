from src.models.candle import Candle
from src.services.sma import SimpleMovingAverage

import pytest


def create_candle(close_price: float) -> Candle:
    return Candle(
        open_time=0,
        open_price=0,
        high_price=0,
        low_price=0,
        close_price=close_price,
        volume=0,
    )


def test_sma_should_calculate_average() -> None:
    sma = SimpleMovingAverage()

    candles = [
        create_candle(10),
        create_candle(20),
        create_candle(30),
    ]

    result = sma.calculate(candles)

    assert result == 20


def test_sma_should_raise_error_when_list_is_empty() -> None:
    sma = SimpleMovingAverage()

    with pytest.raises(
        ValueError,
        match="Lista de candles vazia",
    ):
        sma.calculate([])