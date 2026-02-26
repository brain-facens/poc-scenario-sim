from typing import LiteralString

html_prompt: LiteralString = """
Sua tarefa é receber uma simulação estruturada e convertê-la para uma formatação HTML. Distribua os
campos em sessões e tabelas seguindo o template de exemplo da vector store. Não coloque header nem
footer no seu output, mantenha apenas as tags de formatação. Inclua também o css no seu output.
""".strip()
