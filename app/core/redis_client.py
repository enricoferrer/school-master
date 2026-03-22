import logging
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Retorna cliente Redis singleton. Cria conexão na primeira chamada."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,       # redis://:redispass@redis:6379/0
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Conexão Redis estabelecida")
    return _redis_client


async def close_redis() -> None:
    """Chamado no shutdown da aplicação."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Conexão Redis encerrada")