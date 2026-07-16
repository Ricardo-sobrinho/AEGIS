import json
from pathlib import Path
from typing import Any


VALID_ENVIRONMENTS = {"development", "testing", "production"}


def validate_settings(settings: dict[str, Any]) -> None:
    required_fields = {
        "app_name",
        "version",
        "environment",
        "developer",
        "paper_trading",
    }

    missing_fields = required_fields - settings.keys()

    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        raise ValueError(f"Configurações ausentes: {fields}")

    if not isinstance(settings["app_name"], str) or not settings["app_name"].strip():
        raise ValueError("app_name deve ser um texto não vazio")

    if not isinstance(settings["version"], str) or not settings["version"].strip():
        raise ValueError("version deve ser um texto não vazio")

    if settings["environment"] not in VALID_ENVIRONMENTS:
        raise ValueError(
            "environment deve ser development, testing ou production"
        )

    if not isinstance(settings["developer"], str) or not settings["developer"].strip():
        raise ValueError("developer deve ser um texto não vazio")

    if not isinstance(settings["paper_trading"], bool):
        raise ValueError("paper_trading deve ser true ou false")


def load_settings() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[2]
    settings_file = project_root / "config" / "settings.json"

    if not settings_file.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {settings_file}"
        )

    try:
        with settings_file.open("r", encoding="utf-8") as file:
            settings = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON inválido na linha {error.lineno}, coluna {error.colno}"
        ) from error

    validate_settings(settings)

    return settings