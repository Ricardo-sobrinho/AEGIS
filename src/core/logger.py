import logging
from pathlib import Path


def configure_logger() -> logging.Logger:
    project_root = Path(__file__).resolve().parents[2]
    logs_directory = project_root / "logs"
    logs_directory.mkdir(exist_ok=True)

    log_file = logs_directory / "aegis.log"

    logger = logging.getLogger("aegis")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger