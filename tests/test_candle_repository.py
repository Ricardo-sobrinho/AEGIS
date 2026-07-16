import sqlite3

from src.database.candle_repository import CandleRepository
from src.models.candle import Candle


def create_repository() -> CandleRepository:
    connection = sqlite3.connect(":memory:")
    return CandleRepository(connection)


def create_candle(open_time: int = 1000) -> Candle:
    return Candle(
        open_time=open_time,
        open_price=100.0,
        high_price=110.0,
        low_price=90.0,
        close_price=105.0,
        volume=25.5,
    )


def test_create_table_should_create_candles_table() -> None:
    repository = create_repository()

    repository.create_table()

    result = repository.connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'candles'
        """
    ).fetchone()

    assert result is not None

    repository.connection.close()


def test_save_many_should_insert_candle() -> None:
    repository = create_repository()
    repository.create_table()

    inserted = repository.save_many(
        symbol="BTCUSDT",
        interval="1m",
        candles=[create_candle()],
    )

    total = repository.connection.execute(
        "SELECT COUNT(*) FROM candles"
    ).fetchone()[0]

    assert inserted == 1
    assert total == 1

    repository.connection.close()


def test_duplicate_candle_should_not_be_inserted() -> None:
    repository = create_repository()
    repository.create_table()

    candle = create_candle()

    repository.save_many(
        symbol="BTCUSDT",
        interval="1m",
        candles=[candle],
    )

    inserted_again = repository.save_many(
        symbol="BTCUSDT",
        interval="1m",
        candles=[candle],
    )

    total = repository.connection.execute(
        "SELECT COUNT(*) FROM candles"
    ).fetchone()[0]

    assert inserted_again == 0
    assert total == 1

    repository.connection.close()