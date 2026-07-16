import pytest

from src.core.settings import validate_settings


def create_valid_settings() -> dict:
    return {
        "app_name": "AEGIS",
        "version": "0.8.0",
        "environment": "development",
        "developer": "Ricardo Silva",
        "paper_trading": True,
    }


def test_valid_settings_should_not_raise_error() -> None:
    settings = create_valid_settings()

    validate_settings(settings)


def test_missing_app_name_should_raise_error() -> None:
    settings = create_valid_settings()
    del settings["app_name"]

    with pytest.raises(ValueError, match="Configurações ausentes: app_name"):
        validate_settings(settings)


def test_invalid_paper_trading_type_should_raise_error() -> None:
    settings = create_valid_settings()
    settings["paper_trading"] = "true"

    with pytest.raises(
        ValueError,
        match="paper_trading deve ser true ou false",
    ):
        validate_settings(settings)


def test_invalid_environment_should_raise_error() -> None:
    settings = create_valid_settings()
    settings["environment"] = "local"

    with pytest.raises(
        ValueError,
        match="environment deve ser development, testing ou production",
    ):
        validate_settings(settings)