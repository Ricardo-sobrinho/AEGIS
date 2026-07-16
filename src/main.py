from core.banner import show_banner
from core.logger import configure_logger


def main() -> None:
    show_banner()

    logger = configure_logger()

    logger.info("Inicializando sistema")
    logger.info("Sistema carregado")
    logger.info("Sistema de logs iniciado")

    print()
    print("Bem-vindo, Ricardo.")
    print("AEGIS pronta para iniciar.")


if __name__ == "__main__":
    main()