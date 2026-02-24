# %% Imports
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from typing_extensions import override

# from ..gen_tests.gen_parts.scenario import Scenario


# %% PDF class
class PDF(FPDF):
    @override
    def header(self):
        self.image("../../assets/unifacens-logo.png", w=32, h=32, y=2)
        self.set_font("helvetica", "B", 20)
        self.cell(
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
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")
        return super().footer()


class PDFWriter:
    @staticmethod
    def write() -> str | None:
        file_name: str = (
            f"simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}.pdf"
        )
        pdf: PDF = PDF("P", "mm", "A4")
        pdf.alias_nb_pages()
        pdf.set_title(f"Simulação {datetime.now().strftime('YYYY-MM-dd-hh-mm-ss')}")
        pdf.add_page()
        pdf.set_font("helvetica", "", 16)

        # sections
        PDFWriter._lotta_lines(pdf)

        # check if doc is saved
        if pdf.output(file_name):
            return file_name
        return None

    @staticmethod
    def _lotta_lines(pdf: FPDF) -> FPDF:
        for i in range(41):
            pdf.cell(0, 10, f"Linha {i}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
        return pdf


if __name__ == "__main__":
    file_path = PDFWriter.write()
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
