import sqlite3

from models.candle import Candle


class CandleRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_table(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS candles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            open_time INTEGER NOT NULL,
            open_price REAL NOT NULL,
            high_price REAL NOT NULL,
            low_price REAL NOT NULL,
            close_price REAL NOT NULL,
            volume REAL NOT NULL,
            UNIQUE(symbol, interval, open_time)
        )
        """

        self.connection.execute(query)
        self.connection.commit()

    def save_many(
        self,
        symbol: str,
        interval: str,
        candles: list[Candle],
    ) -> int:
        query = """
        INSERT OR IGNORE INTO candles (
            symbol,
            interval,
            open_time,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        records = [
            (
                symbol,
                interval,
                candle.open_time,
                candle.open_price,
                candle.high_price,
                candle.low_price,
                candle.close_price,
                candle.volume,
            )
            for candle in candles
        ]

        cursor = self.connection.executemany(query, records)
        self.connection.commit()

        return cursor.rowcount