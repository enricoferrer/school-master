from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nota         import Nota
from app.models.avaliacao    import Avaliacao
from app.models.aluno        import Aluno
from app.models.usuario      import Usuario
from app.models.turma_professores import TurmaProfessores
from app.models.disciplina   import Disciplina
from app.models.professor    import Professor
from app.models.funcionario  import Funcionario


class NotaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Avaliações ────────────────────────────────────────────────────────────

    async def criar_avaliacao(self, avaliacao: Avaliacao) -> Avaliacao:
        self.db.add(avaliacao)
        await self.db.commit()
        await self.db.refresh(avaliacao)
        return avaliacao

    async def buscar_avaliacao(self, avaliacao_id: UUID) -> Avaliacao | None:
        result = await self.db.execute(
            select(Avaliacao).where(Avaliacao.id == avaliacao_id)
        )
        return result.scalar_one_or_none()

    # ── Notas ─────────────────────────────────────────────────────────────────

    async def criar_nota(self, nota: Nota) -> Nota:
        self.db.add(nota)
        await self.db.commit()
        await self.db.refresh(nota)
        return nota

    async def buscar_nota(self, nota_id: UUID) -> Nota | None:
        result = await self.db.execute(
            select(Nota).where(Nota.id == nota_id)
        )
        return result.scalar_one_or_none()

    async def buscar_nota_por_aluno_avaliacao(
        self, aluno_id: UUID, avaliacao_id: UUID
    ) -> Nota | None:
        result = await self.db.execute(
            select(Nota).where(
                Nota.fk_aluno     == aluno_id,
                Nota.fk_avaliacao == avaliacao_id,
            )
        )
        return result.scalar_one_or_none()

    async def atualizar_nota(self, nota: Nota, novo_valor: Decimal) -> Nota:
        nota.valor = novo_valor
        await self.db.commit()
        await self.db.refresh(nota)
        return nota

    # ── Ownership: professor → turma ──────────────────────────────────────────

    async def professor_owns_turma(
        self, user_id: str, turma_professor_id: UUID
    ) -> bool:
        """Verifica se o user_id logado é o professor daquela turma/disciplina."""
        result = await self.db.execute(
            select(TurmaProfessores)
            .join(Professor,   Professor.id   == TurmaProfessores.fk_professor)
            .join(Funcionario, Funcionario.id == Professor.fk_funcionario)
            .where(
                TurmaProfessores.id == turma_professor_id,
                Funcionario.fk_usuario == UUID(user_id),
            )
        )
        return result.scalar_one_or_none() is not None

    # ── Notas do aluno para o boletim ─────────────────────────────────────────

    async def notas_do_aluno(
        self,
        aluno_id:   UUID,
        ano_letivo: str,
    ) -> list[dict]:
        """
        Retorna todas as notas do aluno com contexto de disciplina e período.
        """
        result = await self.db.execute(
            select(
                Nota.id.label("nota_id"),
                Nota.valor,
                Avaliacao.peso,
                Avaliacao.periodo,
                Avaliacao.titulo,
                Avaliacao.tipo,
                Disciplina.id.label("disciplina_id"),
                Disciplina.nome.label("disciplina_nome"),
                TurmaProfessores.fk_turma.label("turma_id"),
            )
            .join(Avaliacao,       Avaliacao.id       == Nota.fk_avaliacao)
            .join(TurmaProfessores,  TurmaProfessores.id  == Avaliacao.fk_turma_professor)
            .join(Disciplina,      Disciplina.id       == TurmaProfessores.fk_disciplina)
            .join(
                __import__("app.models.turma", fromlist=["Turma"]).Turma,
                __import__("app.models.turma", fromlist=["Turma"]).Turma.id
                == TurmaProfessores.fk_turma,
            )
            .where(
                Nota.fk_aluno == aluno_id,
                __import__("app.models.turma", fromlist=["Turma"]).Turma.ano_letivo
                == str(ano_letivo),
            )
            .order_by(Disciplina.nome, Avaliacao.periodo)
        )
        rows = result.all()
        return [
            {
                "nota_id":        r.nota_id,
                "valor":          float(r.valor) if r.valor is not None else None,
                "peso":           float(r.peso),
                "periodo":        r.periodo,
                "titulo":         r.titulo,
                "tipo":           r.tipo,
                "disciplina_id":  r.disciplina_id,
                "disciplina_nome":r.disciplina_nome,
                "turma_id":       r.turma_id,
            }
            for r in rows
        ]

    # ── Média da turma por disciplina/período ─────────────────────────────────

    async def media_turma(
        self,
        turma_professor_id: UUID,
        periodo:            str,
    ) -> float:
        """Média ponderada de todos os alunos da turma naquela disciplina/período."""
        result = await self.db.execute(
            select(
                func.sum(Nota.valor * Avaliacao.peso).label("soma_ponderada"),
                func.sum(Avaliacao.peso).label("soma_pesos"),
            )
            .join(Avaliacao, Avaliacao.id == Nota.fk_avaliacao)
            .where(
                Avaliacao.fk_turma_professor == turma_professor_id,
                Avaliacao.periodo            == periodo,
                Nota.valor.isnot(None),
            )
        )
        row = result.one()
        if not row.soma_pesos or float(row.soma_pesos) == 0:
            return 0.0
        return round(float(row.soma_ponderada) / float(row.soma_pesos), 2)

    # ── Analytics por disciplina ──────────────────────────────────────────────

    async def analytics_por_disciplina(
        self,
        periodo: str | None = None,
    ) -> list[dict]:
        """
        Retorna médias individuais de cada aluno por disciplina/período.
        O service calcula os percentis e desvio padrão em Python.
        """
        query = (
            select(
                Disciplina.id.label("disciplina_id"),
                Disciplina.nome.label("disciplina_nome"),
                Avaliacao.periodo,
                Aluno.id.label("aluno_id"),
                Usuario.nome_completo.label("aluno_nome"),
                (
                    func.sum(Nota.valor * Avaliacao.peso)
                    / func.nullif(func.sum(Avaliacao.peso), 0)
                ).label("media_aluno"),
            )
            .join(Avaliacao,      Avaliacao.id      == Nota.fk_avaliacao)
            .join(TurmaProfessores, TurmaProfessores.id == Avaliacao.fk_turma_professor)
            .join(Disciplina,     Disciplina.id     == TurmaProfessores.fk_disciplina)
            .join(Aluno,          Aluno.id          == Nota.fk_aluno)
            .join(Usuario,        Usuario.id        == Aluno.fk_usuario)
            .where(Nota.valor.isnot(None))
            .group_by(
                Disciplina.id, Disciplina.nome,
                Avaliacao.periodo,
                Aluno.id, Usuario.nome_completo,
            )
            .order_by(Disciplina.nome, Avaliacao.periodo)
        )

        if periodo:
            query = query.where(Avaliacao.periodo == periodo)

        rows = (await self.db.execute(query)).all()
        return [
            {
                "disciplina_id":   r.disciplina_id,
                "disciplina_nome": r.disciplina_nome,
                "periodo":         r.periodo,
                "aluno_id":        r.aluno_id,
                "aluno_nome":      r.aluno_nome,
                "media_aluno":     round(float(r.media_aluno), 2),
            }
            for r in rows
        ]