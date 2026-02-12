from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "cosmere_stories.sqlite"
BIBLIOTECA_DIR = BASE_DIR / "biblioteca"
PROMPTS_BACKUP_JSON = (
    BIBLIOTECA_DIR
    / "nacidos-de-la-bruma-era-1"
    / "el-imperio-final"
    / "prompts"
    / "era1_prompts_data.json"
)

IMAGENES_BACKUP_JSON = (
    BIBLIOTECA_DIR
    / "nacidos-de-la-bruma-era-1"
    / "el-imperio-final"
    / "prompts"
    / "imagenes_data.json"
)
