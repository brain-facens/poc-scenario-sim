"""
Module for generating DOCX documents from Scenario instances.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

# Import the generated Pydantic models
from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario


class DocxGenerator:
    """
    Generates a DOCX document based on a Scenario model and a template.
    The generated document preserves the headers and footers of the template
    and creates tables with black borders and light‑blue header shading where
    applicable.
    """

    def __init__(self, template_path: str = ""):
        """
        Initialise the generator with a template DOCX file.

        Args:
            template_path: Path to the template DOCX file.
        """
        path = self._set_template_path(template_path)
        print(path)
        self.doc = Document(path)

    @staticmethod
    def _set_template_path(template_path: str = "") -> Path:
        # Default template path
        if template_path == "":
            template_path = os.path.join(
                os.path.dirname(__file__),
                "..",
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

        return Path(template_path)

    @staticmethod
    def _set_cell_shading(cell, rgb: RGBColor) -> None:
        """
        Apply a solid fill colour to a table cell.

        Args:
            cell: The docx cell to modify.
            rgb: An RGB colour to use as the fill colour.
        """
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        # Use the RGB hex without the leading '#', upper‑cased
        hex_colour = rgb.hex.lstrip("#").upper()
        shd.set(qn("w:fill"), hex_colour)
        tcPr.append(shd)

    def _style_table(self, table) -> None:
        """
        Apply black borders to the table and light‑blue fill to header cells.

        Args:
            table: The docx table to style.
        """
        # Apply black borders to all cells
        tbl = table._tbl
        for tr in tbl.xpath(".//w:tr"):
            tcPr = tr.get_or_add_tcPr()
            tcBorders = OxmlElement("w:tcBorders")
            for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
                border = OxmlElement(f"w:{border_name}")
                border.set(qn("w:val"), "single")
                border.set(qn("w:sz"), "4")
                border.set(qn("w:space"), "0")
                border.set(qn("w:color"), "000000")
                tcPr.append(border)

        # Light‑blue shading for the first row (header)
        first_row = table.rows[0]
        for cell in first_row.cells:
            self._set_cell_shading(cell, RGBColor(173, 216, 230))  # Light blue

    def _add_section(self, title: str, rows: List[tuple]) -> None:
        """
        Add a titled section to the document.

        The section is rendered as a table where the first column contains the
        row labels (e.g. "Objective:", "Quantity:") and the second column
        contains the corresponding values. The first row of the table is used
        as a header and receives light‑blue shading.

        Args:
            title: Title to display at the top of the section.
            rows: List of (label, value) pairs.
        """
        # Create a table with one row for the title and one row per data item
        table = self.doc.add_table(rows=1 + len(rows), cols=2)
        table.style = "Table Grid"
        table.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Populate the title cell (spanning two columns)
        title_cell = table.cell(0, 0)
        title_cell.merge(table.cell(0, 1))
        title_cell.text = title
        title_cell.paragraphs[0].runs[0].font.size = Pt(14)
        title_cell.paragraphs[0].runs[0].font.bold = True
        title_cell.paragraphs[0].runs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Populate the remaining rows with label/value pairs
        for i, (label, value) in enumerate(rows, start=1):
            label_cell = table.cell(i, 0)
            value_cell = table.cell(i, 1)
            label_cell.text = str(label)
            value_cell.text = str(value)

        # Apply styling (borders, header shading)
        self._style_table(table)

    def generate(self, scenario: Scenario, output_path: str) -> str:
        """
        Populate the document with data from a Scenario instance and save it.

        Args:
            scenario: The Scenario model instance containing all data.
            output_path: Path where the generated DOCX should be written.
        """
        # Section: Course Information
        self._add_section(
            "Course Information",
            [
                ("Dia e horário da aula", None),  # Placeholder: to be filled later
                (
                    "Local de realização da aula",
                    None,
                ),  # Placeholder: to be filled later
                ("Nome do cenário", None),  # Placeholder: to be filled later
                ("Tempo de duração", None),  # Placeholder: to be filled later
                ("Curso(s)", None),  # Placeholder: to be filled later
                ("Unidade curricular", None),  # Placeholder: to be filled later
                ("Turma", None),  # Placeholder: to be filled later
                ("Quantidade de estudantes", None),  # Placeholder: to be filled later
                ("Professor", None),  # Placeholder: to be filled later
            ],
        )
        # Section: Learning Objectives
        self._add_section(
            "Learning Objectives",
            [("Objective", scenario.learning_objectives)],
        )

        # Section: Resources
        self._add_section(
            "Resources",
            [(r.name, r.quantity) for r in scenario.necessary_resources],
        )

        # Section: Scene Organization
        self._add_section(
            "Scene Organization",
            [("Description", scenario.scene_organization)],
        )

        # Section: Participants
        participants = scenario.scene_participants
        self._add_section(
            "Participants",
            [
                ("Uses simulator", participants.uses_simulator),
                ("Students quantity", participants.students_quantity),
                ("Actors quantity", participants.actors_quantity),
                ("Students role", participants.students_role),
                ("Actors role", participants.actors_role),
                ("Simulator role", participants.simulator_role),
            ],
        )

        # Section: Case Presentation
        self._add_section(
            "Case Presentation",
            [("Presentation", scenario.case_presentation)],
        )

        # Section: Actor Briefings
        for idx, actor in enumerate(scenario.actor_briefing, start=1):
            self._add_section(
                f"Actor Briefing {idx}",
                [
                    ("Personal data", actor.personal_data),
                    ("Current story", actor.current_story),
                    ("Previous story", actor.previous_story),
                    ("Clothing", actor.clothing),
                    ("Behavior profile", actor.behavior_profile),
                ],
            )

        # Section: Simulator Parameters
        self._add_section(
            "Simulator Parameters",
            [("Parameters", scenario.simulator_parameters)],
        )

        # Section: Evolution Parameters
        self._add_section(
            "Evolution Parameters",
            [("Parameters", scenario.simulator_evolution_parameters)],
        )

        # Section: Students Briefing
        self._add_section(
            "Students Briefing",
            [("Briefing", scenario.students_briefing)],
        )

        # Section: Scene Flow
        for idx, scene in enumerate(scenario.scene_flow, start=1):
            self._add_section(
                f"Scene {idx}",
                [
                    ("Student Plan A", scene.student_plan_a),
                    ("Actor Sim Directions", scene.actor_sim_directions),
                    ("Actor Plan B", scene.actor_plan_b),
                ],
            )

        # Section: Debriefing
        self._add_section(
            "Debriefing",
            [("Debriefing text", scenario.debriefing)],
        )

        # Section: Appendix
        self._add_section(
            "Appendix",
            [("Appendix text", scenario.appendix)],
        )

        # Save the final document
        self.doc.save(output_path)
        return output_path
