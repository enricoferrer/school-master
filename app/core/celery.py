# core/celery.py
from celery import Celery
from kombu import Exchange, Queue
from app.core.config import settings

celery_app = Celery(
    "school_master",
    broker  = settings.rabbitmq_url,
    backend = settings.redis_url,
    include = [
        "app.tasks.attendance_tasks", 
        "app.tasks.grades_tasks",
        "app.tasks.notificacao_tasks",
    ],
)

celery_app.conf.update(
    # ── Serialização ──────────────────────────────────────────────────────────
    task_serializer    = "json",
    result_serializer  = "json",
    accept_content     = ["json"],
    timezone           = "America/Sao_Paulo",
    enable_utc         = True,
    
    # ── Conexão com broker ────────────────────────────────────────────────────
    broker_connection_retry_on_startup = True,
    broker_connection_retry             = True,
    broker_connection_max_retries       = 10,
    
    # ── Filas ─────────────────────────────────────────────────────────────────
    task_routes = {
        "tasks.alertar_frequencia_critica": {"queue": "attendance"},
        "tasks.alertar_nota_editada":       {"queue": "grades"},
        "tasks.disparar_notificacao":       {"queue": "notificacoes"},
        "tasks.processar_notificacao":      {"queue": "notificacoes"},
    },

    task_queues = (
        Queue("attendance", Exchange("attendance"), routing_key="attendance"),
        Queue("grades", Exchange("grades"), routing_key="grades"),
        Queue("notificacoes", Exchange("notificacoes"), routing_key="notificacoes"),
    ),

    # ── Reliability ───────────────────────────────────────────────────────────
    task_reject_on_worker_lost    = True,
    task_acks_late                = True,
    worker_prefetch_multiplier    = 4,
    
    # ── Timeouts e retry ──────────────────────────────────────────────────────
    task_soft_time_limit          = 3600,  # 1 hora
    task_time_limit               = 3700,  # 1h5m (margem para cleanup)
    task_max_retries              = 3,
    
    # ── Performance (workers são síncronos, não async) ────────────────────────
    worker_disable_rate_limits    = False,
    worker_log_format             = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format        = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
)