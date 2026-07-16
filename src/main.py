from core.banner import show_banner
from core.logger import configure_logger
from core.settings import load_settings


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

    print()
    print(f"Bem-vindo, {settings['developer']}.")
    print(f"{settings['app_name']} pronta para iniciar.")


if __name__ == "__main__":
    main()