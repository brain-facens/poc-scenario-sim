#!/usr/bin/env python3
"""
Script to generate DOCX files from Scenario objects using ATA_teste.docx as template.
This script creates a document based on the Scenario model structure while preserving
the template's header and footer and following ABNT formatting standards.
"""

import os
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.shared import Inches, Pt

from modules.scenario_sim.gen_engine.gen_parts.actor_briefing import ActorBriefing
from modules.scenario_sim.gen_engine.gen_parts.participants import Participants
from modules.scenario_sim.gen_engine.gen_parts.resource import Resource
from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.gen_parts.scene import Scene


def create_scenario_docx(
    scenario: Scenario, output_path: str, template_path: str = None
):
    """
    Create a DOCX document from a Scenario object using ATA_teste.docx as template.

    Args:
        scenario (Scenario): The scenario object to convert to DOCX
        output_path (str): Path where the DOCX file will be saved
        template_path (str): Path to the template DOCX file (defaults to assets/Template Cenário_Facens.docx)
    """
    # Default template path
    if template_path is None:
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "assets",
            "Template Cenário_Facens.docx",
        )
        template_path = os.path.abspath(template_path)

    # Check if template exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Load the template document
    doc = Document(template_path)

    # # Set ABNT margins (2.5 cm top, 2.5 cm bottom, 3 cm left, 2 cm right)
    # section = doc.sections[0]
    # section.top_margin = Inches(2.5 / 2.54)  # Convert cm to inches
    # section.bottom_margin = Inches(2.5 / 2.54)
    # section.left_margin = Inches(3 / 2.54)
    # section.right_margin = Inches(2 / 2.54)

    # Set document properties
    doc.core_properties.title = "Cenário de Simulação"
    doc.core_properties.author = "UniFacens"
    doc.core_properties.created = datetime.now()

    # Clear existing content (keep header/footer)
    # Remove all paragraphs except the first (which typically contains header)
    for i in range(len(doc.paragraphs) - 1, -1, -1):
        if i > 0:  # Keep first paragraph (header)
            # Remove the paragraph
            p = doc.paragraphs[i]
            p._p.getparent().remove(p._p)

    # Remove all tables
    for i in range(len(doc.tables) - 1, -1, -1):
        # Remove all tables
        table = doc.tables[i]
        table._tbl.getparent().remove(table._tbl)

    # Add title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("UniFacens - Centro Universitário Facens")
    title_run.bold = True
    title_run.font.size = Pt(24)

    title2 = doc.add_paragraph()
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title2_run = title2.add_run("Cenário de Simulação")
    title2_run.bold = True
    title2_run.font.size = Pt(24)

    # Add a blank line
    doc.add_paragraph()

    # Create main information table (keeping the template structure)
    main_table = doc.add_table(rows=10, cols=2)
    main_table.style = "Table Normal"

    # Add header row
    main_table.cell(0, 0).text = "Dia e horário da aula"
    main_table.cell(0, 1).text = ""

    main_table.cell(1, 0).text = "Local de realização da aula"
    main_table.cell(1, 1).text = ""

    main_table.cell(2, 0).text = "Nome do cenário"
    main_table.cell(2, 1).text = ""

    main_table.cell(3, 0).text = "Tempo de duração"
    main_table.cell(3, 1).text = ""

    main_table.cell(4, 0).text = "Curso(s)"
    main_table.cell(4, 1).text = ""

    main_table.cell(5, 0).text = "Unidade curricular"
    main_table.cell(5, 1).text = ""

    main_table.cell(6, 0).text = "Turma"
    main_table.cell(6, 1).text = ""

    main_table.cell(7, 0).text = "Quantidade de estudantes"
    main_table.cell(7, 1).text = ""

    main_table.cell(8, 0).text = "Professor"
    main_table.cell(8, 1).text = ""

    main_table.cell(9, 0).text = "ROTEIRO DE CENÁRIO DE SIMULAÇÃO"
    main_table.cell(9, 1).text = ""

    # Add learning objectives
    doc.add_paragraph()
    learning_objectives_title = doc.add_paragraph()
    learning_objectives_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    learning_objectives_title_run = learning_objectives_title.add_run(
        "Objetivos de Aprendizagem:"
    )
    learning_objectives_title_run.bold = True
    learning_objectives_title_run.font.size = Pt(14)

    doc.add_paragraph()
    learning_objectives = doc.add_paragraph()
    learning_objectives_run = learning_objectives.add_run(scenario.learning_objectives)
    learning_objectives_run.font.size = Pt(12)

    # Add necessary resources table
    doc.add_paragraph()
    resources_title = doc.add_paragraph()
    resources_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    resources_title_run = resources_title.add_run("Recursos Necessários")
    resources_title_run.bold = True
    resources_title_run.font.size = Pt(14)

    if scenario.necessary_resources:
        resources_table = doc.add_table(
            rows=len(scenario.necessary_resources) + 1, cols=2
        )
        resources_table.style = "Table Normal"

        # Header row
        resources_table.cell(0, 0).text = "Recurso"
        resources_table.cell(0, 1).text = "Quantidade"

        # Data rows
        for i, resource in enumerate(scenario.necessary_resources):
            resources_table.cell(i + 1, 0).text = resource.name
            resources_table.cell(i + 1, 1).text = f"{resource.quantity}x"
    else:
        # Empty resources table
        empty_resources_table = doc.add_table(rows=1, cols=1)
        empty_resources_table.style = "Table Normal"
        empty_resources_table.cell(0, 0).text = "Nenhum recurso necessário"

    # Add scene organization
    doc.add_paragraph()
    scene_org_title = doc.add_paragraph()
    scene_org_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    scene_org_title_run = scene_org_title.add_run("Organização da Cena")
    scene_org_title_run.bold = True
    scene_org_title_run.font.size = Pt(14)

    doc.add_paragraph()
    scene_org = doc.add_paragraph()
    scene_org_run = scene_org.add_run(scenario.scene_organization)
    scene_org_run.font.size = Pt(12)

    # Add participants table
    doc.add_paragraph()
    participants_title = doc.add_paragraph()
    participants_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    participants_title_run = participants_title.add_run("Participantes do cenário")
    participants_title_run.bold = True
    participants_title_run.font.size = Pt(14)

    participants_table = doc.add_table(rows=2, cols=4)
    participants_table.style = "Table Normal"

    # Header row
    participants_table.cell(0, 0).text = "Participante:"
    participants_table.cell(
        0, 1
    ).text = f"Estudante ({scenario.scene_participants.students_quantity})"
    participants_table.cell(
        0, 2
    ).text = f"Ator ({scenario.scene_participants.actors_quantity})"
    participants_table.cell(
        0, 3
    ).text = f"Simulador ({scenario.scene_participants.uses_simulator})"

    # Role row
    participants_table.cell(1, 0).text = "Função no cenário:"
    participants_table.cell(1, 1).text = scenario.scene_participants.students_role
    participants_table.cell(1, 2).text = scenario.scene_participants.actors_role
    participants_table.cell(1, 3).text = scenario.scene_participants.simulator_role

    # Add case presentation
    doc.add_paragraph()
    case_title = doc.add_paragraph()
    case_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    case_title_run = case_title.add_run("Apresentação do Caso")
    case_title_run.bold = True
    case_title_run.font.size = Pt(14)

    doc.add_paragraph()
    case_presentation = doc.add_paragraph()
    case_presentation_run = case_presentation.add_run(scenario.case_presentation)
    case_presentation_run.font.size = Pt(12)

    # Add actor briefings
    for i, actor in enumerate(scenario.actor_briefing, 1):
        doc.add_paragraph()
        actor_title = doc.add_paragraph()
        actor_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        actor_title_run = actor_title.add_run(f"Briefing do ator {i}")
        actor_title_run.bold = True
        actor_title_run.font.size = Pt(14)

        # Add personal data
        personal_data = doc.add_paragraph()
        personal_data_run = personal_data.add_run(
            f"Dados Pessoais:\n\n{actor.personal_data}"
        )
        personal_data_run.font.size = Pt(12)

        # Add current story
        current_story = doc.add_paragraph()
        current_story_run = current_story.add_run(
            f"História atual:\n\n{actor.current_story}"
        )
        current_story_run.font.size = Pt(12)

        # Add previous story
        previous_story = doc.add_paragraph()
        previous_story_run = previous_story.add_run(
            f"História anterior:\n\n{actor.previous_story}"
        )
        previous_story_run.font.size = Pt(12)

        # Add clothing
        clothing = doc.add_paragraph()
        clothing_run = clothing.add_run(f"Vestimenta:\n\n{actor.clothing}")
        clothing_run.font.size = Pt(12)

        # Add behavior profile
        behavior_profile = doc.add_paragraph()
        behavior_profile_run = behavior_profile.add_run(
            f"Perfil de comportamento:\n\n{actor.behavior_profile}"
        )
        behavior_profile_run.font.size = Pt(12)

    # Add simulator parameters
    doc.add_paragraph()
    sim_params_title = doc.add_paragraph()
    sim_params_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    sim_params_title_run = sim_params_title.add_run("Parâmetros do Simulador")
    sim_params_title_run.bold = True
    sim_params_title_run.font.size = Pt(14)

    doc.add_paragraph()
    sim_params = doc.add_paragraph()
    sim_params_run = sim_params.add_run(scenario.simulator_parameters)
    sim_params_run.font.size = Pt(12)

    # Add simulator evolution parameters
    doc.add_paragraph()
    sim_evolution_title = doc.add_paragraph()
    sim_evolution_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    sim_evolution_title_run = sim_evolution_title.add_run(
        "Parâmetros de Evolução do Simulador"
    )
    sim_evolution_title_run.bold = True
    sim_evolution_title_run.font.size = Pt(14)

    doc.add_paragraph()
    sim_evolution = doc.add_paragraph()
    sim_evolution_run = sim_evolution.add_run(scenario.simulator_evolution_parameters)
    sim_evolution_run.font.size = Pt(12)

    # Add students briefing
    doc.add_paragraph()
    students_briefing_title = doc.add_paragraph()
    students_briefing_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    students_briefing_title_run = students_briefing_title.add_run(
        "Briefing dos Estudantes"
    )
    students_briefing_title_run.bold = True
    students_briefing_title_run.font.size = Pt(14)

    doc.add_paragraph()
    students_briefing = doc.add_paragraph()
    students_briefing_run = students_briefing.add_run(scenario.students_briefing)
    students_briefing_run.font.size = Pt(12)

    # Add scene flow
    for i, scene in enumerate(scenario.scene_flow, 1):
        doc.add_paragraph()
        scene_title = doc.add_paragraph()
        scene_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        scene_title_run = scene_title.add_run(f"Cena {i}")
        scene_title_run.bold = True
        scene_title_run.font.size = Pt(14)

        # Student plan A
        student_plan = doc.add_paragraph()
        student_plan_run = student_plan.add_run(f"ESTUDANTE:\n\n{scene.student_plan_a}")
        student_plan_run.font.size = Pt(12)

        # Actor simulation directions
        directions = doc.add_paragraph()
        directions_run = directions.add_run(
            f"ATOR/SIMULADOR:\n\n{scene.actor_sim_directions}"
        )
        directions_run.font.size = Pt(12)

        # Actor plan B
        plan_b = doc.add_paragraph()
        plan_b_run = plan_b.add_run(f"PLANO B:\n\n{scene.actor_plan_b}")
        plan_b_run.font.size = Pt(12)

    # Add debriefing
    doc.add_paragraph()
    debriefing_title = doc.add_paragraph()
    debriefing_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    debriefing_title_run = debriefing_title.add_run("Debriefing")
    debriefing_title_run.bold = True
    debriefing_title_run.font.size = Pt(14)

    doc.add_paragraph()
    debriefing = doc.add_paragraph()
    debriefing_run = debriefing.add_run(scenario.debriefing)
    debriefing_run.font.size = Pt(12)

    # Add appendix
    doc.add_paragraph()
    appendix_title = doc.add_paragraph()
    appendix_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    appendix_title_run = appendix_title.add_run("Anexo")
    appendix_title_run.bold = True
    appendix_title_run.font.size = Pt(14)

    doc.add_paragraph()
    appendix = doc.add_paragraph()
    appendix_run = appendix.add_run(scenario.appendix)
    appendix_run.font.size = Pt(12)

    # Save the document
    doc.save(output_path)
    print(f"Document saved to {output_path}")
    return output_path


# Example usage function
def example_usage():
    """Example of how to use the create_scenario_docx function"""
    # Create a sample scenario for testing
    sample_scenario = Scenario(
        learning_objectives="Compreender os princípios de simulação em ambientes educacionais",
        necessary_resources=[Resource(name="Computador", quantity=1)],
        scene_organization="Cenário de simulação em ambiente hospitalar",
        scene_participants=Participants(
            uses_simulator=True,
            students_quantity=20,
            actors_quantity=5,
            students_role="Pacientes",
            actors_role="Médicos",
            simulator_role="Sistema de simulação",
        ),
        case_presentation="Um paciente apresenta sintomas de dor abdominal intensa...",
        actor_briefing=[
            ActorBriefing(
                personal_data="Nome: João Silva, Idade: 45 anos",
                current_story="Paciente com histórico de doenças cardiovasculares",
                previous_story="Sem histórico de doenças mentais",
                clothing="Roupa de trabalho",
                behavior_profile="Paciente apresenta ansiedade e irritabilidade",
            )
        ],
        simulator_parameters="Parâmetros de simulação: Nível de gravidade médio",
        simulator_evolution_parameters="Evolução do caso: Paciente apresenta melhora gradual",
        students_briefing="Os estudantes devem identificar os sintomas e tomar decisões clínicas",
        scene_flow=[
            Scene(
                student_plan_a="Identificar os sintomas principais do paciente",
                actor_sim_directions="Simular o comportamento do paciente durante a consulta",
                actor_plan_b="Realizar exames complementares conforme necessário",
            )
        ],
        debriefing="Discussão sobre as decisões tomadas durante a simulação",
        appendix="Material complementar para estudo",
        pdf_path="/path/to/pdf",
    )

    # Create the document
    create_scenario_docx(sample_scenario, "sample_scenario.docx")


if __name__ == "__main__":
    example_usage()
