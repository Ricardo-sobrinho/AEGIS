import json
from pathlib import Path
from typing import Any


def load_settings() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[2]
    settings_file = project_root / "config" / "settings.json"

    if not settings_file.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {settings_file}"
        )

    with settings_file.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    return settings