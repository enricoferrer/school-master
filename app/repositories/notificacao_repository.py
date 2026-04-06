# repositories/notificacao_repository.py
from datetime import date, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, case, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aluno             import Aluno
from app.models.aluno_responsavel import AlunoResponsavel
from app.models.avaliacao         import Avaliacao
from app.models.disciplina        import Disciplina
from app.models.frequencia        import Frequencia
from app.models.notificacao       import Notificacao
from app.models.notificacao_preferencia import NotificacaoPreferencia
from app.models.turma_professores   import TurmaProfessores
from app.models.usuario           import Usuario
from app.schemas.notificacao      import PreferenciaCreate


class NotificacaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Notificações ──────────────────────────────────────────────────────────

    async def criar(self, notificacao: Notificacao) -> Notificacao:
        self.db.add(notificacao)
        await self.db.commit()
        await self.db.refresh(notificacao)
        return notificacao

    async def buscar(self, notificacao_id: UUID) -> Notificacao | None:
        result = await self.db.execute(
            select(Notificacao).where(Notificacao.id == notificacao_id)
        )
        return result.scalar_one_or_none()

    async def listar_por_usuario(self, usuario_id: UUID) -> list[Notificacao]:
        result = await self.db.execute(
            select(Notificacao)
            .where(Notificacao.fk_usuario_destino == usuario_id)
            .order_by(Notificacao.criado_em.desc())
        )
        return list(result.scalars().all())

    async def atualizar_status(
        self,
        notificacao_id: UUID,
        status:         str,
        erro_detalhe:   str | None = None,
    ) -> None:
        from datetime import datetime
        valores: dict = {
            "status":     status,
            "tentativas": Notificacao.tentativas + 1,
        }
        if status == "ENVIADO":
            valores["enviado_em"]   = datetime.now(timezone.utc)
            valores["erro_detalhe"] = None
        if erro_detalhe:
            valores["erro_detalhe"] = erro_detalhe

        await self.db.execute(
            update(Notificacao)
            .where(Notificacao.id == notificacao_id)
            .values(**valores)
        )
        await self.db.commit()

    # ── Preferências ──────────────────────────────────────────────────────────

    async def upsert_preferencia(
        self, usuario_id: UUID, pref: PreferenciaCreate
    ) -> NotificacaoPreferencia:
        result = await self.db.execute(
            select(NotificacaoPreferencia).where(
                NotificacaoPreferencia.fk_usuario  == usuario_id,
                NotificacaoPreferencia.canal       == pref.canal,
                NotificacaoPreferencia.tipo_evento == pref.tipo_evento,
            )
        )
        existente = result.scalar_one_or_none()

        if existente:
            existente.ativo          = pref.ativo
            existente.horario_inicio = pref.horario_inicio
            existente.horario_fim    = pref.horario_fim
            await self.db.commit()
            await self.db.refresh(existente)
            return existente

        nova = NotificacaoPreferencia(
            fk_usuario     = usuario_id,
            canal          = pref.canal,
            tipo_evento    = pref.tipo_evento,
            ativo          = pref.ativo,
            horario_inicio = pref.horario_inicio,
            horario_fim    = pref.horario_fim,
        )
        self.db.add(nova)
        await self.db.commit()
        await self.db.refresh(nova)
        return nova

    async def listar_preferencias(
        self, usuario_id: UUID
    ) -> list[NotificacaoPreferencia]:
        result = await self.db.execute(
            select(NotificacaoPreferencia)
            .where(NotificacaoPreferencia.fk_usuario == usuario_id)
        )
        return list(result.scalars().all())

    async def buscar_preferencia(
        self, usuario_id: UUID, tipo_evento: str, canal: str
    ) -> NotificacaoPreferencia | None:
        result = await self.db.execute(
            select(NotificacaoPreferencia).where(
                NotificacaoPreferencia.fk_usuario  == usuario_id,
                NotificacaoPreferencia.tipo_evento == tipo_evento,
                NotificacaoPreferencia.canal       == canal,
            )
        )
        return result.scalar_one_or_none()

    # ── Portal — validação de vínculo ─────────────────────────────────────────

    async def buscar_vinculo(
        self, responsavel_id: UUID, aluno_id: UUID
    ) -> AlunoResponsavel | None:
        result = await self.db.execute(
            select(AlunoResponsavel).where(
                AlunoResponsavel.fk_responsavel == responsavel_id,
                AlunoResponsavel.fk_aluno       == aluno_id,
            )
        )
        return result.scalar_one_or_none()

    # ── Portal — dados do aluno ───────────────────────────────────────────────

    async def dados_portal(self, aluno_id: UUID) -> dict:
        # Nome do aluno
        r_nome = await self.db.execute(
            select(Usuario.nome_completo)
            .join(Aluno, Aluno.fk_usuario == Usuario.id)
            .where(Aluno.id == aluno_id)
        )
        nome = r_nome.scalar_one_or_none() or "Aluno"

        # Notas
        r_notas = await self.db.execute(
            select(
                Disciplina.nome.label("disciplina"),
                Avaliacao.titulo.label("avaliacao"),
                Avaliacao.tipo,
                Avaliacao.periodo,
                Avaliacao.data_aplicacao,
                __import__("app.models.nota", fromlist=["Nota"]).Nota.valor,
                __import__("app.models.nota", fromlist=["Nota"]).Nota.data_lancamento,
            )
            .join(Avaliacao,      Avaliacao.id       == __import__("app.models.nota", fromlist=["Nota"]).Nota.fk_avaliacao)
            .join(TurmaProfessores, TurmaProfessores.id  == Avaliacao.fk_turma_professor)
            .join(Disciplina,     Disciplina.id       == TurmaProfessores.fk_disciplina)
            .where(__import__("app.models.nota", fromlist=["Nota"]).Nota.fk_aluno == aluno_id)
            .order_by(Disciplina.nome, Avaliacao.periodo)
        )

        # Frequência agregada por disciplina
        r_freq = await self.db.execute(
            select(
                Disciplina.nome.label("disciplina"),
                func.count(Frequencia.id).label("total"),
                func.sum(
                    case((Frequencia.presenca == True, 1), else_=0)
                ).label("presencas"),
            )
            .join(TurmaProfessores, TurmaProfessores.id == Frequencia.fk_turma_professor)
            .join(Disciplina,     Disciplina.id     == TurmaProfessores.fk_disciplina)
            .where(Frequencia.fk_aluno == aluno_id)
            .group_by(Disciplina.nome)
        )

        return {
            "nome":        nome,
            "notas":       r_notas.all(),
            "frequencias": r_freq.all(),
        }

    # ── Responsáveis do aluno (para disparar notificações) ───────────────────

    async def responsaveis_do_aluno(self, aluno_id: UUID) -> list[dict]:
        result = await self.db.execute(
            select(
                Usuario.id.label("usuario_id"),
                Usuario.nome_completo,
                Usuario.email,
                AlunoResponsavel.tipo_responsavel,
            )
            .join(AlunoResponsavel, AlunoResponsavel.fk_responsavel == Usuario.id)
            .where(AlunoResponsavel.fk_aluno == aluno_id)
        )
        return [
            {
                "usuario_id":       str(r.usuario_id),
                "nome":             r.nome_completo,
                "email":            r.email,
                "tipo_responsavel": r.tipo_responsavel,
            }
            for r in result.all()
        ]