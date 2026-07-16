from src.core.banner import show_banner
from src.core.event_bus import EventBus
from src.core.logger import configure_logger
from src.core.settings import load_settings
from src.database.candle_repository import CandleRepository
from src.database.connection import get_database_connection
from src.market.binance_client import BinanceMarketClient
from src.market.event_data import CandlesReceivedEvent
from src.market.events import MARKET_CANDLES_RECEIVED
from src.services.candle_storage_handler import CandleStorageHandler


class AegisApplication:
    def __init__(self) -> None:
        self.logger = configure_logger()
        self.settings = load_settings()
        self.market = BinanceMarketClient()
        self.event_bus = EventBus()

    def start(self) -> None:
        show_banner()

        self.logger.info(
            "Inicializando %s",
            self.settings["app_name"],
        )
        self.logger.info(
            "Versão %s",
            self.settings["version"],
        )

        symbol = "BTCUSDT"
        interval = "1m"

        connection = get_database_connection()

        try:
            repository = CandleRepository(connection)
            repository.create_table()

            storage_handler = CandleStorageHandler(repository)

            self.event_bus.subscribe(
                MARKET_CANDLES_RECEIVED,
                storage_handler.handle,
            )

            candles = self.market.get_klines(
                symbol=symbol,
                interval=interval,
                limit=5,
            )

            event = CandlesReceivedEvent(
                symbol=symbol,
                interval=interval,
                candles=candles,
            )

            self.event_bus.publish(
                MARKET_CANDLES_RECEIVED,
                event,
            )

            print()
            print("📊 Mercado conectado.")
            print(f"Candles recebidos: {len(candles)}")
            print("Evento publicado com sucesso.")
        finally:
            connection.close()