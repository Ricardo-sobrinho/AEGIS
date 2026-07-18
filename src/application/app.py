import time

from src.core.banner import show_banner
from src.core.event_bus import EventBus
from src.core.logger import configure_logger
from src.core.settings import load_settings
from src.database.candle_repository import CandleRepository
from src.database.connection import get_database_connection
from src.execution.events import TRADE_REQUESTED
from src.market.binance_client import BinanceMarketClient
from src.market.event_data import CandlesReceivedEvent
from src.market.events import (
    MARKET_CANDLES_RECEIVED,
    STRATEGY_SIGNAL_GENERATED,
)
from src.portfolio.events import PORTFOLIO_UPDATED
from src.risk.events import RISK_OPERATION_APPROVED
from src.services.candle_storage_handler import CandleStorageHandler
from src.services.execution_engine import ExecutionEngine
from src.services.indicator_engine import IndicatorEngine
from src.services.performance_engine import PerformanceEngine
from src.services.portfolio_engine import PortfolioEngine
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
        candle_limit = 5
        update_interval_seconds = 60

        initial_balance = 100000.0

        connection = get_database_connection()

        try:
            repository = CandleRepository(connection)
            repository.create_table()

            storage_handler = CandleStorageHandler(
                repository,
            )

            indicator_engine = IndicatorEngine()

            strategy_engine = StrategyEngine(
                self.event_bus,
            )

            risk_manager = RiskManager(
                event_bus=self.event_bus,
                available_balance=initial_balance,
                minimum_balance=100.0,
            )

            execution_engine = ExecutionEngine(
                event_bus=self.event_bus,
                mode="paper",
                default_quantity=1.0,
            )

            portfolio_engine = PortfolioEngine(
                event_bus=self.event_bus,
                initial_balance=initial_balance,
            )

            performance_engine = PerformanceEngine(
                event_bus=self.event_bus,
                initial_equity=initial_balance,
            )

            self._configure_event_subscriptions(
                storage_handler=storage_handler,
                indicator_engine=indicator_engine,
                strategy_engine=strategy_engine,
                risk_manager=risk_manager,
                execution_engine=execution_engine,
                portfolio_engine=portfolio_engine,
                performance_engine=performance_engine,
            )

            self.logger.info(
                "Market Loop iniciado para %s no intervalo %s.",
                symbol,
                interval,
            )

            self.logger.info(
                "Modo de execução: PAPER."
            )

            print()
            print("🔄 AEGIS em execução contínua.")
            print("Modo de execução: PAPER")
            print("Pressione Ctrl + C para encerrar.")

            while True:
                cycle_started_at = time.monotonic()

                self._process_market_cycle(
                    symbol=symbol,
                    interval=interval,
                    candle_limit=candle_limit,
                )

                cycle_duration = (
                    time.monotonic()
                    - cycle_started_at
                )

                waiting_time = max(
                    0.0,
                    update_interval_seconds
                    - cycle_duration,
                )

                print()
                print(
                    f"⏳ Próxima atualização em "
                    f"{waiting_time:.0f} segundos."
                )

                time.sleep(waiting_time)

        except KeyboardInterrupt:
            print()
            print("🛑 Encerramento solicitado pelo usuário.")

            self.logger.info(
                "AEGIS encerrada pelo usuário."
            )

        except Exception:
            self.logger.exception(
                "Erro durante a execução da AEGIS."
            )
            raise

        finally:
            connection.close()

            self.logger.info(
                "Conexão com o banco de dados encerrada."
            )

    def _configure_event_subscriptions(
        self,
        storage_handler: CandleStorageHandler,
        indicator_engine: IndicatorEngine,
        strategy_engine: StrategyEngine,
        risk_manager: RiskManager,
        execution_engine: ExecutionEngine,
        portfolio_engine: PortfolioEngine,
        performance_engine: PerformanceEngine,
    ) -> None:
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
            performance_engine.handle_market_update,
        )

        self.event_bus.subscribe(
            MARKET_CANDLES_RECEIVED,
            strategy_engine.handle,
        )

        self.event_bus.subscribe(
            STRATEGY_SIGNAL_GENERATED,
            risk_manager.handle,
        )

        self.event_bus.subscribe(
            RISK_OPERATION_APPROVED,
            execution_engine.handle,
        )

        self.event_bus.subscribe(
            TRADE_REQUESTED,
            portfolio_engine.handle,
        )

        self.event_bus.subscribe(
            PORTFOLIO_UPDATED,
            risk_manager.handle_portfolio_update,
        )

        self.event_bus.subscribe(
            PORTFOLIO_UPDATED,
            performance_engine.handle_portfolio_update,
        )

    def _process_market_cycle(
        self,
        symbol: str,
        interval: str,
        candle_limit: int,
    ) -> None:
        print()
        print("=" * 50)
        print("🔎 Nova análise de mercado")
        print("=" * 50)

        candles = self.market.get_klines(
            symbol=symbol,
            interval=interval,
            limit=candle_limit,
        )

        if not candles:
            self.logger.warning(
                "Nenhum candle foi recebido para %s.",
                symbol,
            )
            return

        event = CandlesReceivedEvent(
            symbol=symbol,
            interval=interval,
            candles=candles,
        )

        self.event_bus.publish(
            MARKET_CANDLES_RECEIVED,
            event,
        )

        latest_candle = candles[-1]

        print()
        print("📊 Mercado atualizado")
        print("----------------------------")
        print(f"Ativo...........: {symbol}")
        print(f"Intervalo.......: {interval}")
        print(f"Candles.........: {len(candles)}")
        print(
            f"Último preço....: "
            f"{latest_candle.close_price:.2f}"
        )
        print("Evento publicado: sucesso")