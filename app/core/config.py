from pathlib import Path

from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str
    
    @property
    def JWT_PRIVATE_KEY(self):
        return Path(self.JWT_PRIVATE_KEY_PATH).read_text()

    @property
    def JWT_PUBLIC_KEY(self):
        return Path(self.JWT_PUBLIC_KEY_PATH).read_text()
 
    # Auth / JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
 
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Frequencia
    FREQUENCIA_MINIMA: float = 75.0
    
    # Media para aprovação/reprovação
    MEDIA_APROVADO: float    = 7.0
    MEDIA_RECUPERACAO: float = 5.0
    
    class Config:
        env_file = ".env"
        extra = "ignore"
 
 
settings = Settings()