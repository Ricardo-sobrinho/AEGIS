from src.core.banner import show_banner
from src.core.event_bus import EventBus
from src.core.logger import configure_logger
from src.core.settings import load_settings
from src.database.candle_repository import CandleRepository
from src.database.connection import get_database_connection
from src.market.binance_client import BinanceMarketClient
from src.market.event_data import CandlesReceivedEvent
from src.market.events import (
    MARKET_CANDLES_RECEIVED,
    STRATEGY_SIGNAL_GENERATED,
)
from src.services.candle_storage_handler import CandleStorageHandler
from src.services.indicator_engine import IndicatorEngine
from src.services.risk_manager import RiskManager
from src.services.strategy_engine import StrategyEngine


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
            indicator_engine = IndicatorEngine()
            strategy_engine = StrategyEngine(self.event_bus)
            risk_manager = RiskManager()

            self.event_bus.subscribe(
                MARKET_CANDLES_RECEIVED,
                storage_handler.handle,
            )

            self.event_bus.subscribe(
                MARKET_CANDLES_RECEIVED,
                indicator_engine.handle,
            )

            self.event_bus.subscribe(
                MARKET_CANDLES_RECEIVED,
                strategy_engine.handle,
            )

            self.event_bus.subscribe(
                STRATEGY_SIGNAL_GENERATED,
                risk_manager.handle,
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