# %% Imports
from datetime import datetime

from fpdf import FPDF, Align
from fpdf.enums import VAlign, XPos, YPos
from fpdf.table import Row
from typing_extensions import override

# from ..gen_tests.gen_parts.scenario import Scenario


# %% PDF class
class PDF(FPDF):
    @override
    def header(self):
        _ = self.image("../../assets/unifacens-logo.png", w=32, h=32, y=2)
        self.set_font("helvetica", "B", 20)
        _ = self.cell(
            0,
            10,
            "Simulação de Cenário",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        self.ln(20)
        return super().header()

    @override
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 10)
        _ = self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")
        return super().footer()


class PDFWriter:
    @staticmethod
    def write() -> str | None:
        file_name: str = f"simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}.pdf"
        pdf: PDF = PDF("P", "mm", "A4")
        pdf.alias_nb_pages()
        pdf.set_title(f"Simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}")
        pdf.add_page()
        pdf.set_font("helvetica", "", 16)
        pdf.set_fill_color(66, 135, 245)

        # sections
        pdf = PDFWriter._lotta_lines(pdf)
        pdf = PDFWriter._sim_objective(pdf)
        pdf = PDFWriter._sim_resources(pdf)

        # check if doc is saved
        if pdf.output(file_name):
            return file_name
        return None

    @staticmethod
    def _lotta_lines(pdf: PDF) -> PDF:
        for i in range(41):
            _ = pdf.cell(0, 10, f"Linha {i}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
        return pdf

    @staticmethod
    def _sim_objective(pdf: PDF) -> PDF:
        with pdf.table() as table:
            row: Row = table.row(min_height=40)
            _ = row.cell("Objetivos de aprendizagem", Align.C)
            _ = row.cell()
        pdf.ln(20)

        return pdf

    @staticmethod
    def _sim_resources(pdf: PDF) -> PDF:
        _ = pdf.cell(
            0,
            10,
            "Recursos materiais necessários",
            1,
            fill=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        with pdf.table() as table:
            row: Row = table.row()
            _ = row.cell("MATERIAIS", Align.C, VAlign.T)
            _ = row.cell("QUANTIDADE", Align.C, VAlign.T)
            row = table.row()
            _ = row.cell()
            _ = row.cell()
        return pdf

    @staticmethod
    def from_html(html_data: str) -> str | None:
        file_name: str = f"simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}.pdf"
        pdf: FPDF = FPDF("P", "mm", "A4")
        # pdf.alias_nb_pages()
        # pdf.set_title(f"Simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}")
        pdf.add_page()

        pdf.write_html(html_data)

        # check if doc is saved
        if pdf.output(file_name):
            return file_name
        return None


# %%
if __name__ == "__main__":
    # html testing
    file = open("Template Cenário_Facens.html", "r")
    file_path = PDFWriter.from_html(file.read())
    file.close()
    if file_path:
        print(file_path)

# # %% PDF setup
# file_name = "test.pdf"
# pdf = PDF("P", "mm", "A4")
# pdf.alias_nb_pages()

# pdf.set_title("PDF Teste")
# pdf.set_auto_page_break(auto=True, margin=15)
# pdf.add_page()
# pdf.set_font("helvetica", "", 16)
# for i in range(41):
#     pdf.cell(0, 10, f"Linha {i}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# pdf.ln(2)

# data = (
#     ("Header 1", "Header 2", "Header 3"),
#     ("Row 1, Col 1", "Row 1, Col 2", "Row 1, Col 3"),
#     ("Row 2, Col 1", "Row 2, Col 2", "Row 2, Col 3"),
# )

# with pdf.table() as table:
#     for data_row in data:
#         row = table.row()
#         for datum in data_row:
#             row.cell(datum)


# # %% Save
# pdf.output(file_name)
# print(f"Created {file_name}")

# %%
