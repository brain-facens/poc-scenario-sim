import io
import os
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from ..gen_engine.gen_parts.scenario import Scenario

# Template is stored in poc-scenario-sim/assets/ alongside the other project assets.
# Resolve relative to this file's location so the module is portable.
_MODULE_DIR = Path(__file__).parent.parent  # modules/scenario_sim/
TEMPLATE_PATH = str(
    Path(__file__).parent.parent.parent.parent.parent
    / "assets"
    / "Template Cenário_Facens.docx"
)

NS = (
    'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
    'xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:w10="urn:schemas-microsoft-com:office:word" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
    'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'mc:Ignorable="w14 w15 wp14"'
)


def p(
    text,
    bold=False,
    center=False,
    size=24,
    underline=False,
    justify=True,
    first_line_indent=False,
):
    jc = "center" if center else ("both" if justify else "left")
    u = '<w:u w:val="single"/>' if underline else ""
    b = "<w:b/><w:bCs/>" if bold else ""
    indent = '<w:ind w:firstLine="360"/>' if first_line_indent else ""

    ppr = (
        f'<w:pPr><w:spacing w:line="360" w:lineRule="auto"/>{indent}'
        f'<w:jc w:val="{jc}"/>'
        f'<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        f'{b}<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>{u}'
        f'<w:lang w:val="pt-BR"/></w:rPr></w:pPr>'
    )

    if not text.strip():
        return f"<w:p>{ppr}</w:p>"

    rpr = (
        f'<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        f'{b}<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>{u}'
        f'<w:lang w:val="pt-BR"/></w:rPr>'
    )
    return (
        f"<w:p>{ppr}<w:r>{rpr}"
        f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    )


def p_bullet(text):
    """Parágrafo com bullet point."""
    rpr = (
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
    )
    return (
        f"<w:p>"
        f'<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>'
        f'<w:spacing w:line="360" w:lineRule="auto"/><w:jc w:val="both"/>{rpr}</w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    )


def p_subtitulo_topico(texto):
    """Subtítulo de tópico: I. II. III. em negrito."""
    rpr = (
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        '<w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
    )
    return (
        f'<w:p><w:pPr><w:spacing w:line="360" w:lineRule="auto"/>'
        f'<w:jc w:val="both"/>{rpr}</w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{escape(texto)}</w:t></w:r></w:p>'
    )


def p_item_topico(texto):
    """Item de tópico: a) b) c) com indentação."""
    rpr = (
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
    )
    return (
        f"<w:p><w:pPr>"
        f'<w:ind w:left="720" w:hanging="360"/>'
        f'<w:spacing w:line="360" w:lineRule="auto"/>'
        f'<w:jc w:val="both"/>{rpr}</w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{escape(texto)}</w:t></w:r></w:p>'
    )


def p_deliberacao(texto):
    """Deliberação numerada: 1. 2. 3. com indentação."""
    rpr = (
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
    )
    return (
        f"<w:p><w:pPr>"
        f'<w:ind w:left="720" w:hanging="360"/>'
        f'<w:spacing w:line="360" w:lineRule="auto"/>'
        f'<w:jc w:val="both"/>{rpr}</w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{escape(texto)}</w:t></w:r></w:p>'
    )


def p_assinatura_tabela(participantes):
    """Tabela de assinaturas em duas colunas: linha tracejada + nome."""
    COL_W = 4638
    TABLE_W = COL_W * 2
    LINHA = "________________________________"

    def rpr_cell():
        return (
            '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
            '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
        )

    def tcpr():
        return (
            f'<w:tcPr><w:tcW w:w="{COL_W}" w:type="dxa"/>'
            "<w:tcBorders>"
            '<w:top w:val="none"/><w:left w:val="none"/>'
            '<w:bottom w:val="none"/><w:right w:val="none"/>'
            "</w:tcBorders>"
            "<w:tcMar>"
            '<w:top w:w="200" w:type="dxa"/><w:bottom w:w="400" w:type="dxa"/>'
            '<w:left w:w="200" w:type="dxa"/><w:right w:w="200" w:type="dxa"/>'
            "</w:tcMar></w:tcPr>"
        )

    def celula(nome):
        rp = rpr_cell()
        linha_p = (
            f'<w:p><w:pPr><w:jc w:val="center"/>{rp}</w:pPr>'
            f"<w:r>{rp}<w:t>{escape(LINHA)}</w:t></w:r></w:p>"
        )
        nome_p = (
            f'<w:p><w:pPr><w:jc w:val="center"/>{rp}</w:pPr>'
            f"<w:r>{rp}<w:t>{escape(nome)}</w:t></w:r></w:p>"
        )
        return f"<w:tc>{tcpr()}{linha_p}{nome_p}</w:tc>"

    def celula_vazia():
        return f'<w:tc>{tcpr()}<w:p><w:pPr><w:jc w:val="center"/></w:pPr></w:p></w:tc>'

    lista = list(participantes)
    if len(lista) % 2 != 0:
        lista.append("")

    rows = ""
    for i in range(0, len(lista), 2):
        esq = lista[i]
        dir_ = lista[i + 1]
        c_esq = celula(esq)
        c_dir = celula(dir_) if dir_ else celula_vazia()
        rows += f"<w:tr>{c_esq}{c_dir}</w:tr>"

    return (
        f"<w:tbl>"
        f"<w:tblPr>"
        f'<w:tblW w:w="{TABLE_W}" w:type="dxa"/>'
        f'<w:jc w:val="center"/>'
        f"<w:tblBorders>"
        f'<w:top w:val="none"/><w:left w:val="none"/>'
        f'<w:bottom w:val="none"/><w:right w:val="none"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f"</w:tblBorders></w:tblPr>"
        f"<w:tblGrid>"
        f'<w:gridCol w:w="{COL_W}"/><w:gridCol w:w="{COL_W}"/>'
        f"</w:tblGrid>"
        f"{rows}</w:tbl>"
    )


def build_scenario_document_xml(scenario: Scenario):
    """Build XML for DOCX document based on scenario object."""
    pars = []

    # Títulos
    pars.append(
        p(
            f" cenário: {scenario.learning_objectives[:50]}.",
            bold=True,
            center=True,
            size=28,
        )
    )
    pars.append(
        p("UniFacens - Centro Universitário Facens", bold=True, center=True, size=24)
    )
    pars.append(p("Cenário de Simulação", bold=True, center=True, size=24))
    pars.append(p(""))

    # Case Presentation
    pars.append(p("1. Apresentação do Caso", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.case_presentation.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Scene Organization
    pars.append(p("2. Organização da Cena", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.scene_organization.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Scene Flow
    pars.append(p("3. Desenvolvimento da Cena", bold=True, center=False, size=24))
    pars.append(p(""))
    for i, scene in enumerate(scenario.scene_flow, 1):
        pars.append(p(f"{i}. {scene.student_plan_a}", bold=True, center=False, size=24))
        pars.append(p(""))
        for linha in scene.actor_sim_directions.split("\n"):
            linha = linha.strip()
            if not linha:
                pars.append(p(""))
            elif linha.startswith("- "):
                pars.append(p_bullet(linha[2:].strip()))
            else:
                pars.append(p(linha, justify=True))
        pars.append(p(""))
        if scene.actor_plan_b:
            pars.append(p("Plano do Ator B:", bold=True, center=False, size=24))
            for linha in scene.actor_plan_b.split("\n"):
                linha = linha.strip()
                if not linha:
                    pars.append(p(""))
                elif linha.startswith("- "):
                    pars.append(p_bullet(linha[2:].strip()))
                else:
                    pars.append(p(linha, justify=True))
            pars.append(p(""))

    # Actor Briefing
    pars.append(p("4. Briefing dos Participantes", bold=True, center=False, size=24))
    pars.append(p(""))
    for i, actor in enumerate(scenario.actor_briefing, 1):
        pars.append(p(f"{i}. {actor.personal_data}", bold=True, center=False, size=24))
        pars.append(p(""))
        for linha in actor.current_story.split("\n"):
            linha = linha.strip()
            if not linha:
                pars.append(p(""))
            elif linha.startswith("- "):
                pars.append(p_bullet(linha[2:].strip()))
            else:
                pars.append(p(linha, justify=True))
        pars.append(p(""))

    # Simulator Parameters
    pars.append(p("5. Parâmetros do Simulador", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.simulator_parameters.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Simulator Evolution Parameters
    pars.append(
        p("6. Parâmetros de Evolução do Simulador", bold=True, center=False, size=24)
    )
    pars.append(p(""))
    for linha in scenario.simulator_evolution_parameters.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Students Briefing
    pars.append(p("7. Briefing dos Estudantes", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.students_briefing.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Debriefing
    pars.append(p("8. Debriefing", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.debriefing.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Appendix
    pars.append(p("9. Anexo", bold=True, center=False, size=24))
    pars.append(p(""))
    for linha in scenario.appendix.split("\n"):
        linha = linha.strip()
        if not linha:
            pars.append(p(""))
        elif linha.startswith("- "):
            pars.append(p_bullet(linha[2:].strip()))
        else:
            pars.append(p(linha, justify=True))
    pars.append(p(""))

    # Necessary Resources
    pars.append(p("10. Recursos Necessários", bold=True, center=False, size=24))
    pars.append(p(""))
    for resource in scenario.necessary_resources:
        pars.append(p(f"- {resource.name}: {resource.quantity}", justify=True))
    pars.append(p(""))

    corpo = "\n".join(pars)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document {NS}>
  <w:body>
    {corpo}
    <w:sectPr>
      <w:headerReference w:type="default" r:id="rId7"/>
      <w:footerReference w:type="default" r:id="rId8"/>
      <w:pgSz w:w="11910" w:h="16850"/>
      <w:pgMar w:top="2665" w:right="1134" w:bottom="2127" w:left="1134" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>"""


def generate_scenario_docx(scenario: Scenario) -> bytes:
    """
    Generates a scenario .docx file in memory and returns the raw bytes.

    Uses the Template Cenário_Facens.docx template stored in assets/.
    """
    novo_xml = build_scenario_document_xml(scenario)

    buffer = io.BytesIO()
    with zipfile.ZipFile(TEMPLATE_PATH, "r") as tmpl:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as novo:
            for item in tmpl.namelist():
                if item == "word/document.xml":
                    novo.writestr(item, novo_xml.encode("utf-8"))
                else:
                    novo.writestr(item, tmpl.read(item))

    return buffer.getvalue()


def save_scenario_docx(scenario: Scenario, output_path: str | None = None) -> str:
    """
    Save scenario as a DOCX file.

    Args:
        scenario: Scenario object to convert to DOCX
        output_path: Optional output path. If None, uses scenario.pdf_path

    Returns:
        Path to the saved DOCX file
    """
    if output_path is None:
        output_path = scenario.pdf_path

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate DOCX bytes
    docx_bytes = generate_scenario_docx(scenario)

    # Write to file
    with open(output_path, "wb") as f:
        f.write(docx_bytes)

    return output_path
