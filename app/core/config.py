from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, Any


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ClothShare API"
    
    # Database
    DATABASE_URL: str = "sqlite:///./clothshare.db"  # 개발용 SQLite, 나중에 PostgreSQL로 변경
    
    # JWT
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 개발용, 프로덕션에서 변경 필요
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일
    
    # AWS S3 (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]  # 개발용, 프로덕션에서는 특정 도메인만 허용
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            # Railway가 제공하는 postgres:// 를 postgresql+psycopg2:// 로 변경
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg2://", 1)
            # postgresql:// 도 postgresql+psycopg2:// 로 변경 (명시적 드라이버 지정)
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

