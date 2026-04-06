import logging
import os
import statistics
import uuid
from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from app.core.config import settings
from app.exceptions.NotOwnerException import NotOwnerException
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException
from app.models.avaliacao      import Avaliacao
from app.models.nota           import Nota
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.nota_repository import NotaRepository
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.schemas.nota import (
    NotaCreate, NotaUpdate,
    BoletimResponse, DisciplinaBoletim, MediaPorPeriodo,
    AnalyticsNotasResponse, AnalyticsDisciplina, AlunoAbaixoMedia,
)
from app.schemas.avaliacao import AvaliacaoCreate
from app.services.notificacao_service import NotificacaoService
from app.tasks.grades_tasks import alertar_nota_editada

logger = logging.getLogger("grades")

# ── Regras de negócio ─────────────────────────────────────────────────────────
MEDIA_APROVADO    = settings.MEDIA_APROVADO
MEDIA_RECUPERACAO = settings.MEDIA_RECUPERACAO


def _situacao(media: float) -> str:
    if media >= MEDIA_APROVADO:
        return "Aprovado"
    if media >= MEDIA_RECUPERACAO:
        return "Recuperação"
    return "Reprovado"


def _media_ponderada(notas: list[dict]) -> float:
    """soma(valor * peso) / soma(pesos) — ignora notas None."""
    pares = [(n["valor"], n["peso"]) for n in notas if n["valor"] is not None]
    if not pares:
        return 0.0
    soma_pond = sum(v * p for v, p in pares)
    soma_peso = sum(p for _, p in pares)
    return round(soma_pond / soma_peso, 2) if soma_peso else 0.0


class NotaService:
    def __init__(self, repo: NotaRepository, alunoRepo: AlunoRepository, notificacaoService: NotificacaoService, disciplinaRepo: DisciplinaRepository, turmaProfessorRepo: TurmaProfessoresRepository):
        self.repo = repo
        self.alunoRepo = alunoRepo
        self.notificacaoService = notificacaoService
        self.disciplinaRepo = disciplinaRepo
        self.turmaProfessorRepo = turmaProfessorRepo
    # ── Criar avaliação ───────────────────────────────────────────────────────

    async def criar_avaliacao(
        self, body: AvaliacaoCreate, user_id: str
    ) -> Avaliacao:
        await self._validar_ownership(user_id, body.turma_professor_id)

        avaliacao = Avaliacao(
            id                 = uuid.uuid4(),
            fk_turma_professor = body.turma_professor_id,
            titulo             = body.titulo,
            tipo               = body.tipo,
            peso               = body.peso,
            periodo            = body.periodo,
            data_aplicacao     = body.data_aplicacao,
        )
        return await self.repo.criar_avaliacao(avaliacao)

    # ── Lançar nota ───────────────────────────────────────────────────────────

    async def lancar_nota(self, body: NotaCreate, user_id: str) -> Nota:
        avaliacao = await self._buscar_avaliacao_ou_404(body.avaliacao_id)
        await self._validar_ownership(user_id, avaliacao.fk_turma_professor)

        existente = await self.repo.buscar_nota_por_aluno_avaliacao(
            body.aluno_id, body.avaliacao_id
        )
        if existente:
            raise DuplicateFieldException(
                "Nota já lançada para este aluno nesta avaliação. Use PUT para editar.",
            )

        nota = Nota(
            id           = uuid.uuid4(),
            fk_aluno     = body.aluno_id,
            fk_avaliacao = body.avaliacao_id,
            valor        = body.valor,
        )
        nota = await self.repo.criar_nota(nota)
        aluno_nome = await self._buscar_aluno_nome_ou_404(body.aluno_id)
        turma_professor = await self.turmaProfessorRepo.get_vinculo_by_id(avaliacao.fk_turma_professor)
        disciplina_nome = await self._buscar_disciplina_nome_ou_404(turma_professor.fk_disciplina)

        await self.notificacaoService.notificar_responsaveis(
            aluno_id    = body.aluno_id,
            tipo_evento = "NOTA_LANCADA",
            mensagem    = f"Uma nota foi lançada para o aluno {aluno_nome} na disciplina de {disciplina_nome}: {float(body.valor):.1f}.",
        )
        return nota

    # ── Editar nota (com audit log) ───────────────────────────────────────────

    async def editar_nota(
        self, nota_id: UUID, body: NotaUpdate, user_id: str
    ) -> Nota:
        nota = await self._buscar_nota_ou_404(nota_id)
        avaliacao = await self._buscar_avaliacao_ou_404(nota.fk_avaliacao)
        await self._validar_ownership(user_id, avaliacao.fk_turma_professor)

        valor_anterior = float(nota.valor) if nota.valor is not None else None
        valor_novo     = float(body.valor)

        nota_atualizada = await self.repo.atualizar_nota(nota, body.valor)
        
        aluno_nome = await self._buscar_aluno_nome_ou_404(nota.fk_aluno)
        turma_professor = await self.turmaProfessorRepo.get_vinculo_by_id(avaliacao.fk_turma_professor)
        disciplina_nome = await self._buscar_disciplina_nome_ou_404(turma_professor.fk_disciplina)

        await self.notificacaoService.notificar_responsaveis(
            aluno_id    = nota.fk_aluno,
            tipo_evento = "NOTA_EDITADA",
            mensagem    = f"Uma nota foi editada para o aluno {aluno_nome} na disciplina de {disciplina_nome}, de {float(valor_anterior):.1f} para {float(valor_novo):.1f}.",
        )

        return nota_atualizada

    # ── Boletim ───────────────────────────────────────────────────────────────

    async def boletim(
        self, aluno_id: UUID, ano_letivo: str, aluno_nome: str
    ) -> BoletimResponse:
        notas = await self.repo.notas_do_aluno(aluno_id, ano_letivo)

        if not notas:
            raise NotFoundException("Nenhuma nota encontrada para este aluno no ano letivo informado.")

        # Agrupa: disciplina → período → [notas]
        estrutura: dict[tuple, dict] = defaultdict(lambda: defaultdict(list))
        turma_por_disciplina: dict[UUID, UUID] = {}

        for n in notas:
            chave = (n["disciplina_id"], n["disciplina_nome"])
            estrutura[chave][n["periodo"]].append(n)
            turma_por_disciplina[n["disciplina_id"]] = n["turma_id"]

        disciplinas_boletim = []

        for (disc_id, disc_nome), periodos in estrutura.items():
            bimestres = []
            medias_finais = []

            for periodo in ("1B", "2B", "3B", "4B"):
                notas_periodo = periodos.get(periodo, [])
                if not notas_periodo:
                    continue

                media = _media_ponderada(notas_periodo)
                medias_finais.append(media)

                bimestres.append(MediaPorPeriodo(
                    periodo         = periodo,
                    media_ponderada = media,
                    situacao        = _situacao(media),
                ))

            media_final = round(sum(medias_finais) / len(medias_finais), 2) if medias_finais else 0.0

            tp_id = turma_por_disciplina.get(disc_id)
            media_turma = 0.0
            if tp_id and bimestres:
                media_turma = await self.repo.media_turma(tp_id, bimestres[-1].periodo)

            disciplinas_boletim.append(DisciplinaBoletim(
                disciplina_id   = disc_id,
                disciplina_nome = disc_nome,
                bimestres       = bimestres,
                media_final     = media_final,
                situacao_final  = _situacao(media_final),
                media_turma     = media_turma,
            ))

        return BoletimResponse(
            aluno_id    = aluno_id,
            aluno_nome  = aluno_nome,
            ano_letivo  = ano_letivo,
            disciplinas = disciplinas_boletim,
        )

    # ── Analytics ────────────────────────────────────────────────────────────

    async def analytics(self, periodo: str | None = None) -> AnalyticsNotasResponse:
        rows = await self.repo.analytics_por_disciplina(periodo)

        grupos: dict[tuple, list] = defaultdict(list)
        for r in rows:
            grupos[(r["disciplina_id"], r["disciplina_nome"], r["periodo"])].append(r)

        resultado = []
        for (disc_id, disc_nome, per), alunos in grupos.items():
            medias = [a["media_aluno"] for a in alunos]
            if not medias:
                continue

            media      = round(statistics.mean(medias), 2)
            mediana    = round(statistics.median(medias), 2)
            desvio     = round(statistics.stdev(medias) if len(medias) > 1 else 0.0, 2)
            sorted_m   = sorted(medias)
            n          = len(sorted_m)
            p25        = round(sorted_m[max(0, int(n * 0.25) - 1)], 2)
            p75        = round(sorted_m[min(n - 1, int(n * 0.75))], 2)

            abaixo = [
                AlunoAbaixoMedia(
                    aluno_id   = a["aluno_id"],
                    aluno_nome = a["aluno_nome"],
                    media      = a["media_aluno"],
                )
                for a in alunos if a["media_aluno"] < media
            ]

            resultado.append(AnalyticsDisciplina(
                disciplina_id   = disc_id,
                disciplina_nome = disc_nome,
                periodo         = per,
                media           = media,
                mediana         = mediana,
                desvio_padrao   = desvio,
                percentil_25    = p25,
                percentil_75    = p75,
                alunos_abaixo   = abaixo,
            ))

        return AnalyticsNotasResponse(disciplinas=resultado)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _validar_ownership(self, user_id: str, turma_professor_id: UUID) -> None:
        owns = await self.repo.professor_owns_turma(user_id, turma_professor_id)
        if not owns:
            raise NotOwnerException("Você só pode lançar notas nas turmas em que leciona.")

    async def _buscar_avaliacao_ou_404(self, avaliacao_id: UUID) -> Avaliacao:
        av = await self.repo.buscar_avaliacao(avaliacao_id)
        if not av:
            raise NotFoundException("Avaliação não encontrada.")
        return av

    async def _buscar_nota_ou_404(self, nota_id: UUID) -> Nota:
        n = await self.repo.buscar_nota(nota_id)
        if not n:
            raise NotFoundException("Nota não encontrada.")
        return n
    
    async def _buscar_aluno_nome_ou_404(self, aluno_id: UUID) -> str:
         aluno = await self.alunoRepo.get_aluno_by_id(aluno_id)
         if not aluno:
             raise NotFoundException("Aluno não encontrado.")
         return aluno.usuario.nome_completo
     
    async def _buscar_disciplina_nome_ou_404(self, disciplina_id: UUID) -> str:
        disciplina = await self.disciplinaRepo.get_disciplina_by_id(disciplina_id)
        if not disciplina:
            raise NotFoundException("Disciplina não encontrada.")
        return disciplina.nome