import httpx

from core.banner import show_banner
from core.logger import configure_logger
from core.settings import load_settings
from market.binance_client import BinanceMarketClient


def main() -> None:
    logger = configure_logger()

    try:
        settings = load_settings()
    except (FileNotFoundError, ValueError) as error:
        logger.critical("Falha ao carregar configurações: %s", error)
        return

    show_banner()

    logger.info("Inicializando %s", settings["app_name"])
    logger.info("Versão: %s", settings["version"])
    logger.info("Ambiente: %s", settings["environment"])
    logger.info("Paper trading: %s", settings["paper_trading"])

    market_client = BinanceMarketClient()

    try:
        candles = market_client.get_klines(
            symbol="BTCUSDT",
            interval="1m",
            limit=5,
        )
    except httpx.HTTPError as error:
        logger.error("Falha na comunicação com o mercado: %s", error)
        return
    except ValueError as error:
        logger.error("Dados de mercado inválidos: %s", error)
        return

    print()
    print("📊 Últimos candles de BTCUSDT:")
    print()

    for candle in candles:
        open_price = candle[1]
        high_price = candle[2]
        low_price = candle[3]
        close_price = candle[4]
        volume = candle[5]

        print(
            f"Abertura: {open_price} | "
            f"Máxima: {high_price} | "
            f"Mínima: {low_price} | "
            f"Fechamento: {close_price} | "
            f"Volume: {volume}"
        )

    print()
    print(f"Bem-vindo, {settings['developer']}.")
    print(f"{settings['app_name']} pronta para iniciar.")


if __name__ == "__main__":
    main()