from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_prefix="SCS_")

    app_name: str = "Supply Chain Security Scanner"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = f"sqlite:///{BASE_DIR}/data/scans.db"
    vulnerability_db_path: Path = BASE_DIR / "data" / "vulnerability_db.json"
    reports_dir: Path = BASE_DIR.parent / "reports"
    offline_mode: bool = True
    osv_api_url: str = "https://api.osv.dev/v1"


settings = Settings()
