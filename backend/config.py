from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "sqlite:///./buildflow.db"
    weather_api_key: str = ""
    anthropic_api_key: str = ""
    project_location_lat: float = 33.4484
    project_location_lon: float = -112.0740
    upload_dir: str = str(Path(__file__).parent / "static")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
