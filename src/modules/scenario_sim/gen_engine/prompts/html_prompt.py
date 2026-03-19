from typing import LiteralString

html_prompt: LiteralString = """
Sua tarefa é receber uma simulação estruturada e convertê-la para uma formatação HTML. Distribua os
campos em sessões e tabelas baseando-se no template especificado abaixo. Não altere nenhum texto
que você receber e não tente preencher campos que estão vazios.

Repita os elementos visuais quando for necessário como por exemplo na sessão de briefing do ator, faça um elemento para cada ator.

Esse html será disponibilizado em um arquivo pdf com páginas em tamanho A4, faça com que os elementos visuais do html não fiquem entre uma página e outra e não coloque nada em sua resposta além do html gerado. Não inclua o campo pdf_export no pdf final.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Roteiro de Cenário de Simulação – Facens</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Arial, sans-serif;
      background: #fff;
      color: #000;
      font-size: 11pt;
      line-height: 1.4;
      padding: 28px 36px 48px;
    }

    /* ── MAIN IDENTIFICATION TABLE ── */
    .id-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }

    .id-table td {
      border: 1px solid #000;
      padding: 6px 10px;
      vertical-align: top;
    }

    .id-table td.label {
      font-weight: bold;
      width: 190px;
    }

    .id-table td.value {
      min-height: 24px;
    }

    .id-table .title-row td {
      text-align: center;
      font-weight: bold;
      font-size: 12pt;
      background: #fff;
    }

    /* ── OBJECTIVES BOX ── */
    .obj-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }

    .obj-table td {
      border: 1px solid #000;
      padding: 8px 10px;
      vertical-align: middle;
    }

    .obj-table td.label {
      font-weight: bold;
      text-align: center;
      width: 160px;
    }

    .obj-table td.value {
      min-height: 80px;
    }

    /* ── GENERIC BORDERED BOX ── */
    .box {
      border: 1px solid #000;
      margin-bottom: 20px;
    }

    .box-header {
      font-weight: bold;
      padding: 5px 10px;
      border-bottom: 1px solid #000;
      font-size: 10.5pt;
    }

    .box-hint {
      font-style: italic;
      padding: 2px 10px 6px;
      font-size: 10pt;
      border-bottom: 1px solid #000;
    }

    .box-content {
      padding: 8px 10px;
      min-height: 80px;
      font-size: 11pt;
    }

    .box-content.tall { min-height: 120px; }
    .box-content.short { min-height: 40px; }

    /* ── TWO-COLUMN TABLE (materials, simulator) ── */
    .two-col-table {
      width: 100%;
      border-collapse: collapse;
    }

    .two-col-table th {
      border: 1px solid #000;
      border-top: none;
      padding: 5px 10px;
      font-weight: bold;
      text-align: center;
      background: #fff;
      font-size: 10.5pt;
    }

    .two-col-table th:first-child {
      border-left: none;
    }

    .two-col-table th:last-child {
      border-right: none;
      width: 140px;
    }

    .two-col-table td {
      border: 1px solid #000;
      border-left: none;
      border-right: none;
      padding: 6px 10px;
      min-height: 24px;
      font-size: 11pt;
    }

    .two-col-table td:last-child {
      border-right: none;
      width: 140px;
      border-left: 1px solid #000;
    }

    .two-col-table tr:last-child td {
      border-bottom: none;
    }

    /* ── PARTICIPANTS TABLE ── */
    .part-table {
      width: 100%;
      border-collapse: collapse;
    }

    .part-table th, .part-table td {
      border: 1px solid #000;
      padding: 6px 10px;
      text-align: center;
      font-size: 11pt;
    }

    .part-table th:first-child,
    .part-table td:first-child {
      text-align: left;
      font-weight: bold;
      width: 160px;
    }

    .part-table thead th {
      font-weight: bold;
    }

    /* ── BRIEFING ATOR ── */
    .briefing-table {
      width: 100%;
      border-collapse: collapse;
    }

    .briefing-table td {
      border: 1px solid #000;
      padding: 6px 10px;
      vertical-align: top;
    }

    .briefing-table td.label {
      font-weight: bold;
      width: 160px;
    }

    .briefing-table td.value {
      min-height: 28px;
    }

    /* ── CENA BLOCK ── */
    .cena-title {
      text-align: center;
      font-weight: bold;
      padding: 5px;
      border-bottom: 1px solid #000;
      font-size: 11pt;
    }

    .cena-row-label {
      font-weight: bold;
      padding: 5px 10px;
      border-bottom: 1px solid #000;
      font-size: 10.5pt;
    }

    .cena-row-hint {
      font-style: italic;
      font-weight: normal;
      font-size: 10pt;
    }

    .cena-row-content {
      padding: 8px 10px;
      min-height: 60px;
      border-bottom: 1px solid #000;
      font-size: 11pt;
    }

    .cena-row-content.last {
      border-bottom: none;
    }

    /* ── EDITABLE FIELDS ── */
    [contenteditable="true"] {
      outline: none;
    }

    [contenteditable="true"]:focus {
      background: #fffde7;
    }

    [contenteditable="true"]:empty::before {
      content: attr(data-placeholder);
      color: #bbb;
      font-style: italic;
    }
  </style>
</head>
<body>


  <!-- ── TABELA DE IDENTIFICAÇÃO ── -->
  <table class="id-table">
    <tr class="title-row">
      <td colspan="2">ROTEIRO DE CENÁRIO DE SIMULAÇÃO</td>
    </tr>
    <tr>
      <td class="label">Dia e horário da aula</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Local de realização da aula:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Nome do cenário:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Tempo de duração:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Curso(s):</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Unidade Curricular:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Turma:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Quantidade de estudantes:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
    <tr>
      <td class="label">Professor:</td>
      <td class="value" contenteditable="true"></td>
    </tr>
  </table>

  <!-- ── OBJETIVOS DE APRENDIZAGEM ── -->
  <table class="obj-table" style="margin-bottom:20px">
    <tr>
      <td class="label">Objetivos de<br>aprendizagem:</td>
      <td class="value" style="min-height:90px" contenteditable="true"></td>
    </tr>
  </table>

  <!-- ── RECURSOS MATERIAIS ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header">Recursos materiais necessários:</div>
    <div class="box-hint">(<em>liste o que precisa e a quantidade; se necessário, incluir no anexo, os documentos necessários para o cenário. Exemplo: prontuários, exames, entre outros.</em>)</div>
    <table class="two-col-table">
      <thead>
        <tr>
          <th style="text-align:center">MATERIAIS</th>
          <th style="text-align:center">QUANTIDADE</th>
        </tr>
      </thead>
      <tbody>
        <tr><td contenteditable="true" style="min-height:24px">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ── ORGANIZAÇÃO DO AMBIENTE ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header">Organização do Ambiente:</div>
    <div class="box-hint">(<em>se necessário, incluir fotos que mostram como o ambiente deve estar organizado</em>)</div>
    <div class="box-content tall" contenteditable="true"></div>
  </div>

  <!-- ── PARTICIPANTES DO CENÁRIO ── -->
  <div class="box" style="margin-bottom:20px">
    <table class="part-table">
      <thead>
        <tr>
          <th colspan="4" style="text-align:center; padding:7px">Participantes do cenário</th>
        </tr>
        <tr>
          <th>Participante:</th>
          <th>Estudante (  )</th>
          <th>Ator (  )</th>
          <th>Simulador (  )</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Função no cenário:</td>
          <td contenteditable="true">&nbsp;</td>
          <td contenteditable="true">&nbsp;</td>
          <td contenteditable="true">&nbsp;</td>
        </tr>
        <tr>
          <td>Quantidade:</td>
          <td contenteditable="true">&nbsp;</td>
          <td contenteditable="true">&nbsp;</td>
          <td contenteditable="true">&nbsp;</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ── APRESENTAÇÃO DO CASO ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header">Apresentação do caso:</div>
    <div class="box-hint">(<em>estruture um resumo do cenário, contendo a história e o desfecho esperado</em>)</div>
    <div class="box-content tall" contenteditable="true"></div>
  </div>

  <!-- ── BRIEFING DO ATOR ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header"><em>Briefing</em> do ator:</div>
    <div class="box-hint">(<em>se o cenário ocorrer com a participação de ator</em>)</div>
    <table class="briefing-table">
      <tr>
        <td class="label">a) Dados pessoais:</td>
        <td class="value" contenteditable="true">&nbsp;</td>
      </tr>
      <tr>
        <td class="label">b) História atual:</td>
        <td class="value" contenteditable="true">&nbsp;</td>
      </tr>
      <tr>
        <td class="label">c) História prévia:</td>
        <td class="value" contenteditable="true">&nbsp;</td>
      </tr>
      <tr>
        <td class="label">d) Vestimentas:</td>
        <td class="value" contenteditable="true">&nbsp;</td>
      </tr>
      <tr>
        <td class="label">e) Perfil de comportamento:</td>
        <td class="value" contenteditable="true">&nbsp;</td>
      </tr>
    </table>
  </div>

  <!-- ── PROGRAMAÇÃO DO SIMULADOR (INICIAL) ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header" style="text-align:center">Programação do simulador:<br><em style="font-weight:normal;font-size:10pt">(se necessário)</em></div>
    <table class="two-col-table">
      <thead>
        <tr>
          <th style="text-align:center">Parâmetros de monitorização INICIAL</th>
          <th style="text-align:center">Valores</th>
        </tr>
      </thead>
      <tbody>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ── PROGRAMAÇÃO DO SIMULADOR (EVOLUTIVOS) ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header">Programação evolutivos do simulador:<br><em style="font-weight:normal;font-size:10pt">(se necessário)</em></div>
    <table class="two-col-table">
      <thead>
        <tr>
          <th style="text-align:center">Parâmetros de monitorização EVOLUTIVOS</th>
          <th style="text-align:center">Valores</th>
        </tr>
      </thead>
      <tbody>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
        <tr><td contenteditable="true">&nbsp;</td><td contenteditable="true">&nbsp;</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ── BRIEFING PARA OS ESTUDANTES ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header"><em>Briefing</em> para os estudantes:</div>
    <div class="box-content tall" contenteditable="true"></div>
  </div>

  <!-- ── FLUXO DO CENÁRIO ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header">Fluxo do cenário</div>
    <div class="box-hint">(<em>estruture a sequência de eventos que ocorrerão no cenário, do início ao fim</em>)</div>

    <!-- 1ª CENA -->
    <div class="cena-title">1ª CENA</div>
    <div class="cena-row-label"><strong>ESTUDANTE:</strong> <span class="cena-row-hint">(plano A - o que é esperado que ele fale e/ou execute?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>ATOR/SIMULADOR:</strong> <span class="cena-row-hint">(qual será a reação do ator ou do simulador?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>Plano B</strong> <span class="cena-row-hint">(o que deve ser feito, caso o ESTUDANTE não fale e/ou execute o plano A?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>

    <!-- 2ª CENA -->
    <div class="cena-title">2ª CENA</div>
    <div class="cena-row-label"><strong>ESTUDANTE:</strong> <span class="cena-row-hint">(plano A - o que é esperado que ele fale e/ou execute?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>ATOR/SIMULADOR:</strong> <span class="cena-row-hint">(qual será a reação do ator ou do simulador?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>Plano B</strong> <span class="cena-row-hint">(o que deve ser feito, caso o ESTUDANTE não fale e/ou execute o plano A?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>

    <!-- 3ª CENA -->
    <div class="cena-title">3ª CENA</div>
    <div class="cena-row-label"><strong>ESTUDANTE:</strong> <span class="cena-row-hint">(plano A - o que é esperado que ele fale e/ou execute?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>ATOR/SIMULADOR:</strong> <span class="cena-row-hint">(qual será a reação do ator ou do simulador?)</span></div>
    <div class="cena-row-content" contenteditable="true"></div>
    <div class="cena-row-label"><strong>Plano B</strong> <span class="cena-row-hint">(o que deve ser feito, caso o ESTUDANTE não fale e/ou execute o plano A?)</span></div>
    <div class="cena-row-content last" contenteditable="true"></div>
  </div>

  <!-- ── DEBRIEFING ── -->
  <div class="box" style="margin-bottom:20px">
    <div class="box-header"><em>Debriefing:</em></div>
    <div class="box-hint">(<em>indique o tipo de debriefing que será usado e elabore as perguntas</em>)</div>
    <div class="box-content tall" contenteditable="true"></div>
  </div>

  <!-- ── ANEXOS ── -->
  <div class="box">
    <div class="box-header">Anexos:</div>
    <div class="box-hint">(<em>se necessário, adicione aqui os documentos/imagens que precisam estar presentes no cenário. Ex: prontuário, fichas médicas, receituário, exames de imagem, entre outros.</em>)</div>
    <div class="box-content tall" contenteditable="true"></div>
  </div>

</body>
</html>
```
""".strip()
