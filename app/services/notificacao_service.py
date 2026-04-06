# services/notificacao_service.py
import logging
from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.notificacao_repository import NotificacaoRepository
from app.schemas.notificacao                 import PreferenciaCreate, PreferenciaResponse
from app.schemas.portal                      import (
    PortalAlunoResponse, NotaPortal, FrequenciaPortal,
)
from app.tasks.notificacao_tasks import disparar_notificacao, processar_notificacao

logger = logging.getLogger("notificacoes")

TITULO_EVENTO = {
    "NOTA_LANCADA":       "📝 Nova nota lançada",
    "FALTA":              "⚠️ Falta registrada",
    "FREQUENCIA_CRITICA": "🚨 Frequência abaixo do mínimo",
    "COMUNICADO":         "📢 Novo comunicado escolar",
    "NOTA_EDITADA":       "✏️ Nota editada",
}


class NotificacaoService:
    def __init__(self, repo: NotificacaoRepository):
        self.repo = repo

    # ── Portal do responsável ─────────────────────────────────────────────────

    async def portal_aluno(
        self,
        responsavel_id: UUID,
        aluno_id:       UUID,
    ) -> PortalAlunoResponse:
        vinculo = await self.repo.buscar_vinculo(responsavel_id, aluno_id)
        if not vinculo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem vínculo com este aluno.",
            )

        dados = await self.repo.dados_portal(aluno_id)

        notas = [
            NotaPortal(
                disciplina      = r.disciplina,
                avaliacao       = r.avaliacao,
                tipo            = r.tipo,
                valor           = r.valor,
                periodo         = r.periodo,
                data_lancamento = r.data_lancamento,
            )
            for r in dados["notas"]
        ]

        frequencias = [
            FrequenciaPortal(
                disciplina  = r.disciplina,
                total_aulas = r.total,
                presencas   = r.presencas,
                percentual  = round(r.presencas / r.total * 100 if r.total else 0, 2),
            )
            for r in dados["frequencias"]
        ]

        return PortalAlunoResponse(
            aluno_id         = aluno_id,
            aluno_nome       = dados["nome"],
            tipo_responsavel = vinculo.tipo_responsavel,
            notas            = notas,
            frequencias      = frequencias,
        )

    # ── Disparo de notificações por evento ────────────────────────────────────

    async def notificar_responsaveis(
        self,
        aluno_id:    UUID,
        tipo_evento: str,
        mensagem:    str,
    ) -> None:
        responsaveis = await self.repo.responsaveis_do_aluno(aluno_id)
        titulo       = TITULO_EVENTO.get(tipo_evento, "Notificação escolar")

        for resp in responsaveis:
            pref = await self.repo.buscar_preferencia(
                UUID(resp["usuario_id"]), tipo_evento, "EMAIL"
            )

            if pref and not pref.ativo:
                logger.info(
                    "Notificação suprimida — responsável %s desativou %s",
                    resp["usuario_id"], tipo_evento,
                )
                continue

            horario_inicio = str(pref.horario_inicio) if pref and pref.horario_inicio else None
            horario_fim    = str(pref.horario_fim)    if pref and pref.horario_fim    else None

            disparar_notificacao.delay(
                usuario_id     = resp["usuario_id"],
                email_destino  = resp["email"],
                tipo_evento    = tipo_evento,
                titulo         = titulo,
                mensagem       = mensagem,
                horario_inicio = horario_inicio,
                horario_fim    = horario_fim,
            )

    # ── Reenvio manual ────────────────────────────────────────────────────────

    async def reenviar(self, notificacao_id: UUID) -> dict:
        notif = await self.repo.buscar(notificacao_id)
        if not notif:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notificação não encontrada.")

        if notif.status == "ENVIADO":
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Notificação já foi enviada com sucesso.",
            )

        await self.repo.atualizar_status(notificacao_id, "PENDENTE")

        processar_notificacao.delay(
            notificacao_id = str(notif.id),
            usuario_id     = str(notif.fk_usuario_destino),
            email_destino  = "", 
            titulo         = notif.titulo   or "",
            mensagem       = notif.mensagem or "",
            tipo_evento    = notif.tipo     or "",
            horario_inicio = None,
            horario_fim    = None,
        )
        return {"ok": True, "notificacao_id": str(notificacao_id)}

    # ── Preferências ──────────────────────────────────────────────────────────

    async def salvar_preferencia(
        self, usuario_id: UUID, body: PreferenciaCreate
    ) -> PreferenciaResponse:
        pref = await self.repo.upsert_preferencia(usuario_id, body)
        return PreferenciaResponse.model_validate(pref)

    async def listar_preferencias(
        self, usuario_id: UUID
    ) -> list[PreferenciaResponse]:
        prefs = await self.repo.listar_preferencias(usuario_id)
        return [PreferenciaResponse.model_validate(p) for p in prefs]