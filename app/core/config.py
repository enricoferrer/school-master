from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):
    DATABASE_URL: str
 
    # Auth / JWT
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
 
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
 
    class Config:
        env_file = ".env"
        extra = "ignore"
 
 
settings = Settings()