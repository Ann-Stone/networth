"""Dashboard domain models."""
from app.models.dashboard.fx_rate import FXRate, FXRateCreate, FXRateRead, FXRateUpdate
from app.models.dashboard.stock_price_history import (
    StockPriceHistory,
    StockPriceHistoryCreate,
    StockPriceHistoryRead,
    StockPriceHistoryUpdate,
)
from app.models.dashboard.target_setting import (
    TargetSetting,
    TargetSettingCreate,
    TargetSettingRead,
    TargetSettingUpdate,
)

__all__ = [
    "FXRate",
    "FXRateCreate",
    "FXRateUpdate",
    "FXRateRead",
    "StockPriceHistory",
    "StockPriceHistoryCreate",
    "StockPriceHistoryUpdate",
    "StockPriceHistoryRead",
    "TargetSetting",
    "TargetSettingCreate",
    "TargetSettingUpdate",
    "TargetSettingRead",
]
