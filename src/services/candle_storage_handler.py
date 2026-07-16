from src.database.candle_repository import CandleRepository
from src.market.event_data import CandlesReceivedEvent


class CandleStorageHandler:
    def __init__(self, repository: CandleRepository) -> None:
        self.repository = repository

    def handle(self, event: CandlesReceivedEvent) -> None:
        self.repository.save_many(
            symbol=event.symbol,
            interval=event.interval,
            candles=event.candles,
        )