"""
Utilitários para tasks do Celery - uso de sessões síncronas e async safety.

⚠️  IMPORTANTE SOBRE EVENT LOOPS EM CELERY:
═════════════════════════════════════════════════════════════════════════════

Celery Workers são processos SÍNCRONOS que não têm um event loop do asyncio.
Se você tentar usar código async (AsyncSession, await, etc) em tasks, terá:
    RuntimeError: Task got Future attached to a different loop

SOLUÇÃO: Use SessionLocal (SÍNCRONO) em todas as tasks do Celery:
    from app.core.database import SessionLocal
    
    @celery_app.task
    def minha_task():
        db = SessionLocal()
        try:
            # operações síncronas aqui
            ...
        finally:
            db.close()

═════════════════════════════════════════════════════════════════════════════
"""

from functools import wraps
from contextlib import contextmanager
from app.core.database import SessionLocal


@contextmanager
def get_sync_session():
    """
    Context manager para obter sessão SÍNCRONA seguramente.
    
    Uso:
        @celery_app.task
        def minha_task():
            with get_sync_session() as db:
                # operações de banco aqui
                pass
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


def celery_task_with_db(func):
    """
    Decorator para facilitar o uso de banco em tasks.
    Automatically gerencia a sessão síncrona.
    
    Uso:
        @celery_app.task
        @celery_task_with_db
        def minha_task(db, param1, param2):
            # db já está disponível e será gerenciado
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_sync_session() as db:
            return func(db, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────
# CHECKLIST PARA NOVAS TASKS
# ─────────────────────────────────────────────────────────────────────────
"""
Ao criar uma nova task no Celery, siga:

✅ Imports:
   from app.core.database import SessionLocal  (SÍNCRONO)
   ❌ NÃO use: from app.core.database import AsyncSessionLocal

✅ Dentro da task:
   db = None
   try:
       db = SessionLocal()
       # seu código aqui
   except Exception as exc:
       logger.error(f"Erro: {exc}", exc_info=True)
       if db:
           db.rollback()
       raise self.retry(exc=exc)
   finally:
       if db:
           db.close()

✅ Não use:
   ❌ async def minha_task()
   ❌ await algo
   ❌ async with AsyncSessionLocal() as db
   ❌ from asgiref.sync import async_to_sync  (causa o erro!)

✅ Para chamar tasks paralelas:
   task1.delay(arg1)
   task2.delay(arg2)
   # Celery cuida de rodar em paralelo
"""
