from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://rentcredit:rentcredit@localhost:5432/rentcredit"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "supersecret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_CLIENT_ID: str = ""
    STRIPE_RESIDENT_PRICE_ID: str = ""

    # Pricing
    RESIDENT_MONTHLY_FEE_CENTS: int = 895  # $8.95
    PM_MONTHLY_PAYOUT_CENTS: int = 300     # $3.00
    FREE_TRIAL_DAYS: int = 30

    # Email
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@rentreport.com"

    # Credit Bureaus
    EXPERIAN_FTP_HOST: str = ""
    EXPERIAN_FTP_USER: str = ""
    EXPERIAN_FTP_PASSWORD: str = ""
    EQUIFAX_FTP_HOST: str = ""
    EQUIFAX_FTP_USER: str = ""
    EQUIFAX_FTP_PASSWORD: str = ""
    TRANSUNION_FTP_HOST: str = ""
    TRANSUNION_FTP_USER: str = ""
    TRANSUNION_FTP_PASSWORD: str = ""

    # PMS
    REALPAGE_API_KEY: str = ""
    REALPAGE_API_URL: str = "https://api.realpage.com"
    YARDI_API_KEY: str = ""
    YARDI_API_URL: str = "https://api.yardipcv.com"
    APPFOLIO_CLIENT_ID: str = ""
    APPFOLIO_CLIENT_SECRET: str = ""
    APPFOLIO_API_URL: str = "https://api.appfolio.com"
    ENTRATA_API_KEY: str = ""
    ENTRATA_API_URL: str = "https://api.entrata.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
