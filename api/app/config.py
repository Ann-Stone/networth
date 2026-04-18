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

    invoice_card_no: str = ""
    invoice_password: str = ""
    invoice_app_id: str = ""
    invoice_skip_path: str = "config/invoice_skip.json"
    merchant_mapping_path: str = "config/merchant_mapping.json"
    import_csv: str = ""


settings = Settings()
