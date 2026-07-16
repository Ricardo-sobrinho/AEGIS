import sqlite3
from pathlib import Path


def get_database_connection() -> sqlite3.Connection:
    project_root = Path(__file__).resolve().parents[2]
    database_directory = project_root / "data"
    database_directory.mkdir(exist_ok=True)

    database_file = database_directory / "aegis.db"

    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row

    return connection