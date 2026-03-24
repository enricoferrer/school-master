# utils/pdf_generator.py

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf_frequencia(dados: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # ── Título ─────────────────────────────────────────────
    elements.append(Paragraph("Relatório de Frequência Escolar", styles["Title"]))
    elements.append(Spacer(1, 12))

    periodo = dados.get("periodo", {})
    elements.append(
        Paragraph(
            f"Período: {periodo.get('inicio')} até {periodo.get('fim')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 16))

    # ── Top faltas ─────────────────────────────────────────
    elements.append(Paragraph("Top 10 Alunos com Mais Faltas", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    top_faltas = dados.get("top_faltas", [])

    table_data = [["#", "Aluno", "Faltas"]]

    for i, aluno in enumerate(top_faltas):
        table_data.append([
            str(i + 1),
            aluno["aluno_nome"],
            str(aluno["total_faltas"]),
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#175e7a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ── Tendência ──────────────────────────────────────────
    elements.append(Paragraph("Tendência de Frequência por Turma", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    tendencia = dados.get("tendencia", [])

    table_data = [[
        "Turma",
        "Semana",
        "Total",
        "Presenças",
        "% Frequência"
    ]]

    for t in tendencia:
        percentual = t["percentual"]
        table_data.append([
            t["turma_id"],
            t["semana"],
            str(t["total"]),
            str(t["presencas"]),
            f"{percentual}%",
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#175e7a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)

    # ── Build PDF ─────────────────────────────────────────
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf