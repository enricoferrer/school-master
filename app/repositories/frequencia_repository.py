from datetime import date
from uuid import UUID

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.frequencia import Frequencia
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.turma_professores import TurmaProfessores
from app.models.disciplina import Disciplina
from app.models.aluno_responsavel import AlunoResponsavel


class FrequenciaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Escrita ──────────────────────────────────────────────────────────────

    async def registrar(self, frequencia: Frequencia) -> Frequencia:
        self.db.add(frequencia)
        await self.db.commit()
        await self.db.refresh(frequencia)
        return frequencia

    # ── Leitura básica ────────────────────────────────────────────────────────

    async def buscar_por_aluno_turma_data(
        self,
        aluno_id: UUID,
        turma_professor_id: UUID,
        data: date,
    ) -> Frequencia | None:
        result = await self.db.execute(
            select(Frequencia).where(
                Frequencia.fk_aluno == aluno_id,
                Frequencia.fk_turma_professor == turma_professor_id,
                Frequencia.data == data,
            )
        )
        return result.scalar_one_or_none()

    # ── Índice de frequência de um aluno ─────────────────────────────────────

    async def calcular_frequencia_aluno(
        self,
        aluno_id: UUID,
        turma_professor_id: UUID,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        query = select(
            func.count(Frequencia.id).label("total"),
            func.sum(
                case((Frequencia.presenca == True, 1), else_=0)
            ).label("presencas"),
        ).where(
            Frequencia.fk_aluno == aluno_id,
            Frequencia.fk_turma_professor == turma_professor_id,
        )

        if data_inicio:
            query = query.where(Frequencia.data >= data_inicio)
        if data_fim:
            query = query.where(Frequencia.data <= data_fim)

        row = (await self.db.execute(query)).one()

        total = row.total or 0
        presencas = row.presencas or 0
        percentual = (presencas / total * 100) if total > 0 else 0.0

        return {
            "total_aulas": total,
            "total_presencas": presencas,
            "percentual": round(percentual, 2),
        }

    # ── Responsáveis do aluno ────────────────────────────────────────────────

    async def buscar_responsaveis(self, aluno_id: UUID) -> list[dict]:
        result = await self.db.execute(
            select(Usuario.nome_completo, Usuario.email)
            .join(AlunoResponsavel, AlunoResponsavel.fk_responsavel == Usuario.id)
            .where(AlunoResponsavel.fk_aluno == aluno_id)
        )

        return [
            {"nome": r.nome_completo, "email": r.email}
            for r in result.all()
        ]

    # ── Analytics: absenteísmo por turma ─────────────────────────────────────

    async def absenteismo_por_turma(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[dict]:
        faltas_case = case((Frequencia.presenca == False, 1), else_=0)

        query = (
            select(
                TurmaProfessores.fk_turma.label("turma_id"),
                Disciplina.nome.label("disciplina"),
                func.count(Frequencia.id).label("total_aulas"),
                func.sum(faltas_case).label("total_faltas"),
                (
                    func.sum(faltas_case) * 100.0
                    / func.nullif(func.count(Frequencia.id), 0)
                ).label("taxa_absenteismo"),
            )
            .join(TurmaProfessores, TurmaProfessores.id == Frequencia.fk_turma_professor)
            .join(Disciplina, Disciplina.id == TurmaProfessores.fk_disciplina)
            .group_by(TurmaProfessores.fk_turma, Disciplina.nome)
            .order_by(func.sum(faltas_case).desc())
        )

        if data_inicio:
            query = query.where(Frequencia.data >= data_inicio)
        if data_fim:
            query = query.where(Frequencia.data <= data_fim)

        rows = (await self.db.execute(query)).all()

        return [
            {
                "turma_id": str(r.turma_id),
                "disciplina": r.disciplina,
                "total_aulas": r.total_aulas,
                "total_faltas": r.total_faltas,
                "taxa_absenteismo": round(float(r.taxa_absenteismo or 0), 2),
            }
            for r in rows
        ]

    # ── Analytics: top alunos com mais faltas ────────────────────────────────

    async def top_faltas(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        limit: int = 10,
    ) -> list[dict]:
        query = (
            select(
                Aluno.id.label("aluno_id"),
                Usuario.nome_completo.label("aluno_nome"),
                func.count(Frequencia.id).label("total_faltas"),
            )
            .join(Aluno, Aluno.id == Frequencia.fk_aluno)
            .join(Usuario, Usuario.id == Aluno.fk_usuario)
            .where(Frequencia.presenca == False)
            .group_by(Aluno.id, Usuario.nome_completo)
            .order_by(func.count(Frequencia.id).desc())
            .limit(limit)
        )

        if data_inicio:
            query = query.where(Frequencia.data >= data_inicio)
        if data_fim:
            query = query.where(Frequencia.data <= data_fim)

        rows = (await self.db.execute(query)).all()

        return [
            {
                "aluno_id": str(r.aluno_id),
                "aluno_nome": r.aluno_nome,
                "total_faltas": r.total_faltas,
            }
            for r in rows
        ]

    # ── Tendência de frequência (para gráficos/relatórios) ───────────────────

    async def tendencia_frequencia_por_turma(
    self,
    data_inicio: date,
    data_fim: date,
) -> list[dict]:

        semana = func.date_trunc("week", Frequencia.data)

        query = (
            select(
                TurmaProfessores.fk_turma.label("turma_id"),
                semana.label("semana"),
                func.count(Frequencia.id).label("total"),
                func.sum(
                    case((Frequencia.presenca == True, 1), else_=0)
                ).label("presencas"),
            )
            .join(TurmaProfessores, TurmaProfessores.id == Frequencia.fk_turma_professor)
            .where(
                and_(
                    Frequencia.data >= data_inicio,
                    Frequencia.data <= data_fim
                )
            )
            .group_by(
                TurmaProfessores.fk_turma,
                semana 
            )
            .order_by(
                TurmaProfessores.fk_turma,
                semana 
            )
        )

        rows = (await self.db.execute(query)).all()

        return [
            {
                "turma_id": str(r.turma_id),
                "semana": r.semana.strftime("%Y-%m-%d"),
                "total": r.total,
                "presencas": r.presencas,
                "percentual": round(
                    float(r.presencas / r.total * 100) if r.total else 0,
                    2
                ),
            }
            for r in rows
        ]