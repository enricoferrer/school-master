import json
import logging
from typing import Set

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.redis_client import get_redis
from app.core.permissions import ROLE_PERMISSIONS
from app.models.role_permissions import RolePermission
from app.repositories.role_permission_repository import RolePermissionRepository

logger = logging.getLogger(__name__)

PERMISSIONS_CACHE_TTL = 300  # 5 minutos (US-002)


async def get_permissions_for_role(
    role_name: str,
    repo: RolePermissionRepository,
) -> Set[str]:
    redis     = await get_redis()
    cache_key = f"rbac:perms:{role_name.upper()}"

    # ── 1. Cache ──────────────────────────────────────────────
    try:
        cached = await redis.get(cache_key)
        if cached:
            logger.info("RBAC cache hit | role=%s", role_name)
            return set(json.loads(cached))
    except Exception as exc:
        logger.warning("Redis indisponível, usando DB. Erro: %s", exc)

    # ── 2. Fallback: repositório ──────────────────────────────
    permissions = await repo.get_permissions_by_role_name(role_name)
    logger.info("RBAC DB query | role=%s | count=%d", role_name, len(permissions))

    # ── 3. Grava no cache ─────────────────────────────────────
    try:
        await redis.setex(cache_key, PERMISSIONS_CACHE_TTL, json.dumps(list(permissions)))
    except Exception as exc:
        logger.warning("Erro ao gravar cache Redis. Erro: %s", exc)

    return permissions


async def invalidate_role_cache(role_name: str) -> None:
    """
    Invalida o cache de um papel.
    Chamado após ROLE_ASSIGN ou ROLE_REVOKE.
    """
    try:
        redis = await get_redis()
        deleted = await redis.delete(f"rbac:perms:{role_name.upper()}")
        logger.info("Cache RBAC invalidado | role=%s | deleted=%d", role_name, deleted)
    except Exception as exc:
        logger.warning("Falha ao invalidar cache RBAC: %s", exc)


async def seed_role_permissions(db: AsyncSession) -> None:
    """
    Popula roles + role_permissions no startup se estiverem vazios.
    Idempotente — seguro chamar toda vez que a aplicação sobe.
    """
    from app.models.role import Role

    for role_name, permissions in ROLE_PERMISSIONS.items():

        # Garante que o papel existe
        role = await db.scalar(select(Role).where(Role.nome == role_name))
        if not role:
            role = Role(nome=role_name)
            db.add(role)
            await db.flush()
            logger.info("Papel criado: %s", role_name)

        # Busca permissões já existentes para esse papel
        result = await db.execute(
            select(RolePermission.permission).where(RolePermission.fk_role == role.id)
        )
        existing: Set[str] = {row[0] for row in result.all()}

        # Insere somente as que faltam
        new_permissions = permissions - existing
        for perm in new_permissions:
            db.add(RolePermission(fk_role=role.id, permission=perm))

        if new_permissions:
            logger.info("Permissões adicionadas | role=%s | count=%d", role_name, len(new_permissions))

    await db.commit()
    logger.info("Seed de role_permissions concluído")