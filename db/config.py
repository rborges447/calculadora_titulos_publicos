from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1] # raiz do projeto
DB_PATH = PROJECT_ROOT / "data" / "app.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"