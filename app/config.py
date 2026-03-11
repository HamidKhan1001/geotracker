import os

class Config:
    APP_NAME     = "GeoTracker"
    VERSION      = "1.0.0"
    DEBUG        = os.getenv("DEBUG", "false").lower() == "true"
    PORT         = int(os.getenv("PORT", 5000))
    IPAPI_BASE   = "https://ipapi.co"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
    RATE_LIMIT   = os.getenv("RATE_LIMIT", "30 per minute")
    SECRET_KEY   = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
