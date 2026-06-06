from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    app_name: str = "Networth API"
    debug: bool = True
    port: int = 9528
    database_url: str = "sqlite:///~/.networth/networth.db"
    # Run the FX/stock month-end backfill on startup (disabled in tests).
    enable_startup_catch_up: bool = True

    invoice_card_no: str = ""
    invoice_password: str = ""
    invoice_app_id: str = ""
    invoice_skip_path: str = "config/invoice_skip.json"
    merchant_mapping_path: str = "config/merchant_mapping.json"
    invoice_error_log: str = "logs/invoice_import_errors.log"


settings = Settings()
