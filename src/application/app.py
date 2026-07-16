from core.banner import show_banner
from core.logger import configure_logger
from core.settings import load_settings
from database.candle_repository import CandleRepository
from database.connection import get_database_connection
from market.binance_client import BinanceMarketClient


class AegisApplication:
    def __init__(self) -> None:
        self.logger = configure_logger()
        self.settings = load_settings()
        self.market = BinanceMarketClient()

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

        candles = self.market.get_klines(
            symbol=symbol,
            interval=interval,
            limit=5,
        )

        connection = get_database_connection()

        try:
            repository = CandleRepository(connection)
            repository.create_table()

            inserted_records = repository.save_many(
                symbol=symbol,
                interval=interval,
                candles=candles,
            )
        finally:
            connection.close()

        print()
        print("📊 Mercado conectado.")
        print(f"Candles recebidos: {len(candles)}")
        print(f"Candles novos salvos: {inserted_records}")
        print()

        for candle in candles:
            print(
                f"Abertura: {candle.open_price:.2f} | "
                f"Máxima: {candle.high_price:.2f} | "
                f"Mínima: {candle.low_price:.2f} | "
                f"Fechamento: {candle.close_price:.2f} | "
                f"Volume: {candle.volume:.8f}"
            )