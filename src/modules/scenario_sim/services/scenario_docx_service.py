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
    Path(__file__).parent.parent.parent.parent.parent / "assets" / "ATA_teste.docx"
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


def build_table_xml(
    num_rows, num_columns, content, orientation="vertical", has_headers=True
):
    """Build XML for a table with specified dimensions and content."""
    # Define table properties
    # Use page width (11910 dxa) as reference for table width and column width
    TABLE_W = 11910
    COL_W = TABLE_W // num_columns

    def rpr_cell():
        return (
            '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
            '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/></w:rPr>'
        )

    def tcpr(color=None):
        borders = (
            '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        )
        tcw = f'<w:tcW w:w="{COL_W}" w:type="dxa"/>'
        if color:
            return (
                f"<w:tcPr>{tcw}"
                f"<w:tcBorders>{borders}</w:tcBorders>"
                f'<w:shd w:val="clear" w:color="auto" w:fill="{color}"/>'
                "<w:tcMar>"
                '<w:top w:w="200" w:type="dxa"/><w:bottom w:w="200" w:type="dxa"/>'
                '<w:left w:w="200" w:type="dxa"/><w:right w:w="200" w:type="dxa"/>'
                "</w:tcMar></w:tcPr>"
            )
        else:
            return (
                f"<w:tcPr>{tcw}"
                f"<w:tcBorders>{borders}</w:tcBorders>"
                "<w:tcMar>"
                '<w:top w:w="200" w:type="dxa"/><w:bottom w:w="200" w:type="dxa"/>'
                '<w:left w:w="200" w:type="dxa"/><w:right w:w="200" w:type="dxa"/>'
                "</w:tcMar></w:tcPr>"
            )

    def celula(texto, is_header=False):
        rp = rpr_cell()
        if is_header:
            rp = (
                '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
                '<w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR"/>'
                '<w:color w:val="000000"/></w:rPr>'
            )
        color = "#748fa3" if is_header else None
        tcpr_xml = tcpr(color)
        jc = "center" if is_header else "left"
        return (
            f"<w:tc>{tcpr_xml}"
            f'<w:p><w:pPr><w:jc w:val="{jc}"/>{rp}</w:pPr>'
            f"<w:r>{rp}<w:t>{escape(texto)}</w:t></w:r></w:p>"
            "</w:tc>"
        )

    # Prepare rows
    rows = ""
    for i in range(num_rows):
        row = "<w:tr>"
        for j in range(num_columns):
            if (
                has_headers
                and (orientation == "vertical" and i == 0)
                or (orientation == "horizontal" and j == 0)
            ):
                # Header row or column
                is_header = True
            else:
                is_header = False

            if orientation == "vertical":
                # Each row is a list of data from the content
                cell_content = (
                    content[i][j] if i < len(content) and j < len(content[i]) else ""
                )
            else:  # horizontal
                # Each column is a list of data from the content
                cell_content = (
                    content[j][i] if j < len(content) and i < len(content[j]) else ""
                )

            row += celula(cell_content, is_header)
        row += "</w:tr>"
        rows += row

    # Build table XML
    table_xml = "<w:tbl><w:tblPr>"
    if num_columns == 1:
        # Make table fill the page horizontally when there's only one column
        table_xml += '<w:tblW w:w="11910" w:type="pct"/>'
    else:
        table_xml += f'<w:tblW w:w="{TABLE_W}" w:type="pct"/>'
    table_xml += (
        '<w:jc w:val="center"/>'
        "<w:tblBorders>"
        '<w:top w:val="none"/><w:left w:val="none"/>'
        '<w:bottom w:val="none"/><w:right w:val="none"/>'
        '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        "</w:tblBorders></w:tblPr>"
        "<w:tblGrid>"
    )
    for _ in range(num_columns):
        table_xml += f'<w:gridCol w:w="{COL_W}"/>'
    table_xml += "</w:tblGrid>"
    table_xml += rows
    table_xml += "</w:tbl>"

    return table_xml


def build_scenario_document_xml(scenario: Scenario):
    """Build XML for DOCX document based on scenario object."""
    pars = []

    # Títulos
    pars.append(
        p("UniFacens - Centro Universitário Facens", bold=True, center=True, size=24)
    )
    pars.append(p("Cenário de Simulação", bold=True, center=True, size=24))
    pars.append(p(""))

    # Table definition
    fields = [
        "Dia e horário da aula",
        "Local de realização da aula",
        "Nome do cenário",
        "Tempo de duração",
        "Curso(s)",
        "Unidade curricular",
        "Turma",
        "Quantidade de estudantes",
        "Professor",
    ]

    # Create table content
    table_content = []
    table_content.append(["ROTEIRO DE CENÁRIO DE SIMULAÇÃO", ""])
    for field in fields:
        table_content.append([field, ""])

    table_xml = build_table_xml(
        num_rows=len(fields),
        num_columns=2,
        content=table_content,
        orientation="vertical",
        has_headers=True,
    )

    pars.append(p(""))
    pars.append(table_xml)
    pars.append(p(""))

    # Learning Objectives
    table_content = []
    table_content.append(["Objetivos de Aprendizagem:", ""])
    table_content.append(["", scenario.learning_objectives])

    if table_content:
        table_xml = build_table_xml(
            num_rows=1,
            num_columns=len(table_content),
            content=table_content,
            orientation="horizontal",
            has_headers=True,
        )
        pars.append(table_xml)
    else:
        pars.append(p(""))

    # Necessary Resources
    pars.append(p(""))
    table_content = []
    table_content.append(["Recursos Necessários", " Quantidade"])
    for resource in scenario.necessary_resources:
        table_content.append([f"- {resource.name}", f"{resource.quantity}x"])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=2,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    pars.append(p(""))

    # Scene Organization
    pars.append(p(""))

    # Split scene organization into lines and create table
    table_content = []
    table_content.append(["Organização da Cena", ""])
    table_content.append([scenario.scene_organization, ""])

    if table_content:  # Only create table if there's content
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    else:
        pars.append(p(""))

    # Participants
    pars.append(p(""))
    table_content = []
    table_content.append(["Participantes do cenário", "", "", ""])
    table_content.append(
        [
            "Participante:",
            f"Estudante ({scenario.scene_participants.students_quantity})",
            f"Ator ({scenario.scene_participants.actors_quantity})",
            f"Simulador ({scenario.scene_participants.uses_simulator})",
        ]
    )
    table_content.append(
        [
            "Função no cenário:",
            scenario.scene_participants.students_role,
            scenario.scene_participants.actors_role,
            scenario.scene_participants.simulator_role,
        ]
    )

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=4,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    else:
        pars.append(p(""))

    # Case Presentation
    # Split case presentation into lines and create table
    pars.append(p(""))
    lines = scenario.case_presentation.split("\n")
    table_content = []
    table_content.append(["Apresentação do Caso", ""])
    for linha in lines:
        linha = linha.strip()
        if linha:  # Only add non-empty lines
            if linha.startswith("- "):
                table_content.append([linha[2:].strip(), ""])
            else:
                table_content.append([linha, ""])

    if table_content:  # Only create table if there's content
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    else:
        pars.append(p(""))

    # Actor Briefing
    pars.append(p(""))
    for i, actor in enumerate(scenario.actor_briefing, 1):
        # Create table header
        table_content = []
        table_content.append([f"Briefing do ator {i}", ""])

        # Personal data
        personal_data = f"Dados Pessoais:\n\n{actor.personal_data}"
        table_content.append([personal_data, ""])

        # Current story
        current_story = f"História atual:\n\n{actor.current_story}"
        table_content.append([current_story, ""])

        # Previous story
        previous_story = f"História anterior:\n\n{actor.previous_story}"
        table_content.append([previous_story, ""])

        # Clothing
        clothing = f"Vestimenta:\n\n{actor.clothing}"
        table_content.append([clothing, ""])

        # Split actor's behavior profile into lines
        lines = actor.behavior_profile.split("\n")
        # Join all non-empty lines into a single string to be displayed with "behavior profile"
        behavior_profile = f"Perfil de comportamento:\n\n{actor.behavior_profile}"
        table_content.append([behavior_profile, ""])

        if table_content:
            table_xml = build_table_xml(
                num_rows=len(table_content),
                num_columns=1,
                content=table_content,
                orientation="vertical",
                has_headers=True,
            )
            pars.append(table_xml)
        pars.append(p(""))

    # Simulator Parameters
    pars.append(p(""))
    lines = scenario.simulator_parameters.split("\n")
    table_content = []
    table_content.append(["Parâmetros do Simulador", ""])
    simulator_parameters = " ".join(linha.strip() for linha in lines if linha.strip())
    if simulator_parameters:
        table_content.append([simulator_parameters, ""])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    pars.append(p(""))

    # Simulator Evolution Parameters
    pars.append(p(""))
    lines = scenario.simulator_evolution_parameters.split("\n")
    table_content = []
    table_content.append(["Parâmetros de Evolução do Simulador", ""])
    simulator_evolution = " ".join(linha.strip() for linha in lines if linha.strip())
    if simulator_evolution:
        table_content.append([simulator_evolution, ""])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    pars.append(p(""))

    # Students Briefing
    pars.append(p(""))
    lines = scenario.students_briefing.split("\n")
    table_content = []
    table_content.append(["Briefing dos Estudantes", ""])
    students_briefing = " ".join(linha.strip() for linha in lines if linha.strip())
    if students_briefing:
        table_content.append([students_briefing, ""])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    pars.append(p(""))

    # Scene Flow
    for i, scene in enumerate(scenario.scene_flow, 1):
        # Table for each scene
        pars.append(p(""))

        # Create table content for this scene
        table_content = []
        table_content.append([f"Cena {i}"])
        # Student Plan A
        student_plan_text = f"ESTUDANTE:\n\n{scene.student_plan_a}"
        table_content.append([student_plan_text, ""])

        # Actor Simulation Directions
        directions_text = f"ATOR/SIMULADOR:\n\n{scene.actor_sim_directions}"
        table_content.append([directions_text, ""])

        # Actor Plan B
        plan_b_text = f"PLANO B:\n\n{scene.actor_plan_b}"
        table_content.append([plan_b_text, ""])

        # Build table
        if table_content:
            table_xml = build_table_xml(
                num_rows=len(table_content),
                num_columns=1,
                content=table_content,
                orientation="vertical",
                has_headers=True,
            )
            pars.append(table_xml)
        pars.append(p(""))

    # Debriefing
    pars.append(p(""))
    lines = scenario.debriefing.split("\n")
    table_content = []
    table_content.append(["Debriefing", ""])
    debriefing = " ".join(linha.strip() for linha in lines if linha.strip())
    if debriefing:
        table_content.append([debriefing, ""])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
    pars.append(p(""))

    # Appendix
    pars.append(p(""))
    lines = scenario.appendix.split("\n")
    table_content = []
    table_content.append(["Anexo", ""])
    appendix = " ".join(linha.strip() for linha in lines if linha.strip())
    if appendix:
        table_content.append([appendix, ""])

    if table_content:
        table_xml = build_table_xml(
            num_rows=len(table_content),
            num_columns=1,
            content=table_content,
            orientation="vertical",
            has_headers=True,
        )
        pars.append(table_xml)
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
