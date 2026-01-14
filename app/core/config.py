from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cache
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 애플리케이션 기본 설정
    PROJECT_NAME: str = "FastAPI Community"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 보안 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 데이터 저장소 설정
    DATA_DIR: str = "./data"
    USE_DATABASE: bool = False
    DATABASE_URL: Optional[str] = "sqlite:///./community.db"
    
    # MongoDB 설정
    # MONGODB_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",        # .env 파일을 읽어옴
        case_sensitive=True,    # 대소문자 구분
        extra="ignore"         # 정의되지 않은 환경변수가 있어도 에러내지 않고 무시
    )

@cache
def get_settings() -> Settings:
    return Settings()