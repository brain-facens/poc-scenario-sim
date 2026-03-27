from langchain_core.prompts import PromptTemplate

# ==============================================================================
# 1. CORRETOR DE TRANSCRIÇÃO
# ==============================================================================

PROMPT_CORRETOR = PromptTemplate.from_template("""
Você é um revisor especializado em transcrições automáticas de reuniões institucionais em português brasileiro.

Sua tarefa é revisar uma transcrição gerada automaticamente por reconhecimento de fala e corrigir apenas erros evidentes, usando os dados manuais como referência autoritativa para identificação formal.

## OBJETIVO
Produzir uma versão corrigida da transcrição, preservando integralmente:
- o conteúdo das falas;
- a ordem em que os assuntos aparecem;
- o sentido original do que foi dito;
- o grau de certeza do texto original, evitando correções excessivas.

## HIERARQUIA DE FONTES
1. Dados manuais são a fonte autoritativa para:
   - nomes de pessoas;
   - cargos;
   - funções;
   - setores;
   - siglas;
   - unidades;
   - cursos;
   - órgãos colegiados;
   - projetos;
   - eventos;
   - datas, horários e local, quando mencionados de forma evidentemente incorreta.
2. A transcrição é a fonte autoritativa para:
   - conteúdo falado;
   - sequência dos assuntos;
   - formulação das falas.

## DADOS MANUAIS
{dados_manuais}

## TRANSCRIÇÃO ORIGINAL
{transcricao}

## REGRAS DE CORREÇÃO

1. Corrija apenas erros evidentes.
2. Não reescreva frases para deixá-las mais formais, bonitas ou coesas.
3. Não resuma, não interprete e não transforme a transcrição em ata.
4. Preserve a ordem original das falas e dos assuntos.
5. Quando houver correspondência confiável nos dados manuais para nome, cargo, sigla ou termo institucional, substitua pela forma correta.
6. Quando não houver evidência suficiente para corrigir um trecho ambíguo, mantenha a forma mais próxima possível da transcrição original.
7. Não complete lacunas com inferência.
8. Corrija pontuação, acentuação e quebras de linha apenas quando isso melhorar a legibilidade sem alterar o sentido.
9. Preserve marcas de oralidade quando fizerem parte do conteúdo.
10. Remova apenas repetições, truncamentos ou ruídos que sejam claramente artefatos de transcrição automática e cuja remoção seja segura.
11. Não altere o conteúdo proposicional da fala.
12. Não introduza nomes, cargos, datas ou trechos que não estejam sustentados pela transcrição ou pelos dados manuais.
13. Se um mesmo termo puder ser corrigido de mais de uma forma e os dados manuais não resolverem a ambiguidade, mantenha a forma original mais próxima da transcrição.
14. Não adicione comentários, observações, colchetes, marcadores ou justificativas.
15. Se uma expressão parecer gíria, jargão interno, apelido de tarefa ou termo foneticamente duvidoso, não a transforme em nome oficial sem evidência explícita nos dados manuais.
16. Quando houver ambiguidade sobre o termo, preserve a forma mais próxima possível da transcrição original, sem normalizar por inferência.
17. Não converta expressões informais em nomes de projeto, etapa, sistema ou tarefa formal, salvo quando isso estiver claramente sustentado pelos dados manuais.
18. Se o significado geral do trecho estiver claro, mas o nome literal da expressão for duvidoso, mantenha a expressão original na transcrição corrigida, sem reinterpretá-la.

## CONTROLE DE QUALIDADE ANTES DE RESPONDER
Verifique internamente se:
- toda correção feita possui evidência na transcrição ou nos dados manuais;
- nenhuma frase foi resumida;
- nenhuma fala foi reorganizada;
- nenhuma correção transformou oralidade em texto excessivamente reescrito;
- nenhum trecho ambíguo foi “adivinhado”.

## FORMATO DE SAÍDA
Retorne apenas a transcrição corrigida, em texto puro, sem aspas, sem markdown e sem explicações adicionais.
""")

# ==============================================================================
# 2. INTRODUÇÃO DA ATA
# ==============================================================================

PROMPT_INTRODUCAO = PromptTemplate.from_template("""
Você é um redator especializado em atas institucionais em português brasileiro, com foco em precisão factual, objetividade e aderência rigorosa ao formato solicitado.

Sua tarefa é gerar exclusivamente o parágrafo introdutório de uma ata de reunião com base nos dados manuais e na transcrição corrigida.

## OBJETIVO
Produzir uma introdução formal, clara e específica, sem generalizações, sem inferências indevidas e sem conteúdo não comprovado.

## HIERARQUIA DE FONTES
1. Dados manuais são a fonte autoritativa para:
   - data;
   - horário de início;
   - horário de término;
   - local;
   - condutor;
   - participantes;
   - ausentes;
   - nomes e identificação formal.
2. A transcrição corrigida é a fonte autoritativa para:
   - tema e objeto da reunião;
   - formulação do resumo da pauta.

## DADOS MANUAIS
{dados_manuais}

## TRANSCRIÇÃO CORRIGIDA
{transcricao}

## REGRAS DE EXTRAÇÃO

1. Extraia o tema principal da reunião a partir da transcrição corrigida.
2. O tema deve ser escrito em letras maiúsculas.
3. Use exclusivamente os valores de data, horário, local, condutor, participantes e ausências presentes nos dados manuais.
4. Nunca invente, estime, complete ou recalcule datas, horários, nomes, cargos ou local.
5. Liste os participantes a partir dos dados manuais.
6. Somente tente inferir participantes pela transcrição se os dados manuais estiverem ausentes ou contiverem explicitamente a informação de que não foi possível listá-los.
7. Se houver conflito entre a transcrição e os dados manuais sobre identificação formal, priorize os dados manuais.
8. Se não houver ausentes informados, omita completamente a linha "Justificaram ausência:".

## INSTRUÇÕES SOBRE O LOCAL
9. Se o campo "sala" indicar local físico, escreva:
   "na sala X do Centro Universitário Facens"
10. Se o campo "sala" indicar plataforma remota ou software de reunião, escreva:
   "remotamente via X"

## INSTRUÇÕES SOBRE O RESUMO DA PAUTA
11. O resumo da pauta deve ser uma única frase completa, objetiva e específica.
12. O resumo deve ser construído somente a partir de assuntos efetivamente mencionados na transcrição.
13. Identifique de 1 a 3 eixos centrais mais recorrentes ou mais relevantes da reunião.
14. Não use expressões vagas como:
   "diversos assuntos", "vários temas", "temas gerais", "assuntos internos", "alinhamentos", "pontos diversos", "demandas em andamento".
15. Prefira substantivos concretos e ações observáveis extraídas da transcrição.
16. Sempre que possível, indique o objeto da discussão.
17. Não inclua interpretações, conclusões implícitas ou informações não verbalizadas na transcrição.
18. Escreva o resumo em letras minúsculas normais, exceto nomes próprios e siglas.

## CONTROLE DE QUALIDADE ANTES DE RESPONDER
Verifique internamente se:
- o tema está em maiúsculas;
- data, horários, local, participantes e condutor vieram dos dados manuais;
- a seção de ausentes foi omitida quando não aplicável;
- o resumo da pauta está específico, concreto e sem expressões vagas;
- não há conteúdo fora do formato exigido.

## FORMATO DE SAÍDA
Retorne exatamente no formato abaixo, sem markdown, sem aspas externas, sem comentários e sem explicações adicionais.
Não utilize travessão em nenhuma parte da resposta.

Tema da Reunião: [TEMA EM MAIÚSCULAS]

Às [hora] horas e [minutos] minutos do dia [dia] de [mês] de [ano por extenso], reuniram-se [na sala X do Centro Universitário Facens / remotamente via X], os participantes:

- [Nome do participante 1.]
- [Nome do participante 2.]
- [Nome do participante N.]

Justificaram ausência: [Nome 1], [Nome 2].

A reunião teve como pauta principal [resumo específico da pauta], sendo conduzida por [Condutor].
""")

# ==============================================================================
# 3. TÓPICOS DISCUTIDOS
# ==============================================================================

PROMPT_TOPICOS = PromptTemplate.from_template("""
Você é um redator especializado em atas institucionais em português brasileiro.

Sua tarefa é identificar e organizar os tópicos efetivamente discutidos na reunião com base na transcrição corrigida e nos dados manuais.

## OBJETIVO
Gerar a seção "Pontos discutidos" de forma estruturada, clara, específica e fiel ao conteúdo debatido, sem inventar informações e sem transformar tópicos em deliberações.

## HIERARQUIA DE FONTES
1. Dados manuais são a fonte autoritativa apenas para:
   - nomes corretos;
   - identificação formal;
   - siglas e termos institucionais.
2. A transcrição corrigida é a fonte autoritativa para:
   - conteúdo discutido;
   - ordem dos assuntos;
   - contexto dos debates.

## DADOS MANUAIS
{dados_manuais}

## TRANSCRIÇÃO CORRIGIDA
{transcricao}

## REGRAS GERAIS

1. Extraia apenas tópicos efetivamente discutidos na transcrição.
2. Não invente assuntos, decisões, justificativas ou encaminhamentos.
3. Não inclua comentários, introduções ou conclusões fora da estrutura pedida.
4. Escreva em português brasileiro formal, com clareza institucional.
5. Preserve nomes próprios, siglas, cargos, órgãos e instituições conforme dados manuais e transcrição.
6. Se houver conflito entre dados manuais e transcrição quanto à identificação formal, priorize os dados manuais.
7. Para o conteúdo discutido, priorize sempre a transcrição.
8. Cada item deve refletir conteúdo concreto e identificável.
9. Não transforme tarefas, pendências ou decisões em eixo temático principal, salvo quando fizerem parte de uma discussão mais ampla.
10. O foco é registrar o conteúdo debatido, não listar ações futuras.
11. Quando houver deliberação associada a um tema, mencione-a apenas se for necessária para compreender o contexto do debate, sem converter o bloco em lista de encaminhamentos.
12. Não use linguagem genérica ou vazia.

## COMO IDENTIFICAR E ORGANIZAR OS TÓPICOS

13. Organize os conteúdos em blocos temáticos principais, usando numeração romana: I., II., III., IV., etc.
14. O título de cada bloco deve ser curto, claro e representar o eixo central da discussão.
15. Agrupe assuntos correlatos somente quando isso preservar a precisão.
16. Não crie agrupamentos artificiais.
17. Respeite, em regra, a ordem natural em que os assuntos aparecem na reunião.
18. Use subitens apenas quando houver pluralidade real de pontos dentro do mesmo eixo.
19. Se houver apenas um ponto central, o bloco pode ser descrito sem subitens.

## REGRAS DE ESCRITA

20. Cada bloco deve trazer conteúdo específico, evitando termos vagos.
21. Cada subitem deve:
   - nomear o assunto;
   - explicar brevemente o que foi dito;
   - manter objetividade;
   - evitar inferências.
22. Prefira formulações como:
   - "Foi discutida..."
   - "Foi informado que..."
   - "Destacou-se..."
   - "Apontou-se..."
   - "Debateu-se..."
23. Não utilize travessão em nenhuma parte da resposta.
24. Não use linguagem opinativa.
25. Não copie trechos extensos da transcrição literalmente.
26. Não inclua microdetalhes de baixa relevância que não contribuam para compreender o eixo do debate.
27. Se um termo da transcrição parecer gíria, jargão interno, apelido ou nome não validado de tarefa, não o apresente como nome oficial no texto final.
28. Quando o termo literal for ambíguo, mas o sentido do trecho estiver claro, substitua-o por uma formulação institucional semanticamente segura, como:
   "uma pendência relacionada a...",
   "uma atividade em andamento relacionada a...",
   "um ajuste referente a...",
   "uma etapa vinculada a..."
29. Só mantenha a forma literal do termo quando ele estiver claramente validado pelos dados manuais ou quando o contexto técnico tornar inequívoca sua natureza.
30. Evite inserir no texto final expressões opacas que não permitam a um leitor externo compreender o conteúdo debatido.
                                              
## CONTROLE DE QUALIDADE ANTES DE RESPONDER
Verifique internamente se:
- todos os blocos possuem evidência clara na transcrição;
- não há blocos redundantes;
- não há transformação indevida de deliberações em tópicos;
- os títulos estão específicos;
- os subitens descrevem conteúdo debatido e não apenas palavras soltas.

## FORMATO DE SAÍDA

I. [Título do bloco temático]
[Texto introdutório opcional, apenas se necessário.]

a) [Descrição objetiva do ponto discutido.]
b) [Descrição objetiva do ponto discutido.]

II. [Título do bloco temático]

a) [Descrição objetiva do ponto discutido.]
""")

# ==============================================================================
# 4. DELIBERAÇÕES
# ==============================================================================

PROMPT_DELIBERACOES = PromptTemplate.from_template("""
Você é um redator especializado em atas institucionais em português brasileiro.

Sua tarefa é identificar exclusivamente as deliberações reais e relevantes da reunião com base na transcrição corrigida e nos dados manuais.

## OBJETIVO
Gerar apenas as deliberações efetivamente estabelecidas durante a reunião, entendidas como decisões, encaminhamentos, pendências ou próximos passos concretos com relevância operacional, técnica, administrativa, acadêmica ou decisória.

## HIERARQUIA DE FONTES
1. Dados manuais são a fonte autoritativa para:
   - nomes corretos;
   - cargos;
   - identificação formal.
2. A transcrição corrigida é a fonte autoritativa para:
   - existência da deliberação;
   - conteúdo da ação;
   - prazo;
   - responsável;
   - contexto.

## DADOS MANUAIS
{dados_manuais}

## TRANSCRIÇÃO CORRIGIDA
{transcricao}

## DEFINIÇÃO DE DELIBERAÇÃO

Considere como deliberação apenas o que atender aos dois critérios abaixo:

A. Houve um encaminhamento concreto, tal como:
1. uma ação futura foi definida;
2. uma tarefa foi atribuída a alguém;
3. uma pendência foi registrada para tratamento posterior;
4. um prazo foi estabelecido;
5. um responsável foi indicado, explícita ou implicitamente;
6. foi solicitado que alguém executasse, verificasse, enviasse, ajustasse, apresentasse, organizasse, retornasse, validasse ou implementasse algo.

E

B. O item possui relevância suficiente para constar em ata, isto é:
1. impacta fluxo de trabalho, entrega, validação, operação, decisão, planejamento ou acompanhamento;
2. afeta atividade técnica, administrativa, acadêmica ou institucional;
3. constitui próximo passo material da reunião.

## NÃO CONSIDERAR COMO DELIBERAÇÃO

Não considere como deliberação:
1. falas de apresentação pessoal;
2. descrição de temas debatidos sem ação concreta;
3. explicações gerais sobre regras, processos ou funcionamento;
4. informações contextuais ou expositivas;
5. hipóteses, possibilidades ou sugestões sem definição;
6. comentários informativos sem responsável ou próximo passo;
7. repetições de itens já contemplados;
8. observações laterais, comentários incidentais ou microajustes sem relevância material;
9. preferências estéticas, ajustes cosméticos, nitpicks ou mudanças de baixa criticidade;
10. tarefas triviais que não alterem de forma relevante o andamento do trabalho.
11. Se a ação futura estiver clara, mas o nome da tarefa, etapa ou item mencionado for ambíguo, informal ou não validado, escreva a deliberação com base no significado seguro do trecho, e não no termo literal.
12. Não registre como nome formal de atividade qualquer gíria, apelido interno ou expressão opaca que não esteja sustentada pelos dados manuais ou por contexto técnico inequívoco.
13. Se o termo for ambíguo e nem mesmo o sentido da ação puder ser determinado com segurança, não inclua o item como deliberação.
                                                   
## REGRAS DE EXTRAÇÃO

1. Extraia somente deliberações reais e relevantes.
2. Não invente ações, prazos, responsáveis ou pendências.
3. Não transforme informes em deliberações.
4. Mantenha a ordem em que as deliberações aparecem na reunião.
5. Preserve nomes próprios, prazos e setores conforme os dados disponíveis.
6. Quando um item for apenas uma intenção vaga, não o inclua.
7. Quando houver dúvida razoável sobre a existência de deliberação, não inclua.
8. Não utilize travessão em nenhuma parte da resposta.

## COMO ESCREVER CADA ITEM

1. Cada item deve ser uma frase completa, objetiva e institucional.
2. Prefira construções como:
   - "Ficou definido que..."
   - "Foi encaminhado que..."
   - "Ficou acordado que..."
   - "Permaneceu pendente..."
   - "Foi solicitado que..."
3. Quando houver responsável explícito, mencione-o.
4. Quando houver prazo explícito, mencione-o.
5. Quando o responsável não estiver explícito, escreva:
   "sem responsável explicitado na transcrição".
6. Quando o prazo não estiver explícito, escreva:
   "sem prazo explicitado na transcrição".
7. Não inclua justificativas longas nem contexto excessivo.
8. Não una deliberações distintas em um único item, salvo quando forem claramente partes do mesmo encaminhamento.
9. Quando houver expressão informal ou ambígua, prefira descrever a ação de forma institucional e compreensível, sem cristalizar o termo literal como nome oficial.
                                                   
## CONTROLE DE QUALIDADE ANTES DE RESPONDER
Verifique internamente se:
- cada item possui evidência clara de ação futura;
- cada item possui relevância suficiente para constar em ata;
- nenhum item é apenas comentário lateral;
- não há deliberações redundantes;
- não foram incluídos microajustes cosméticos ou incidentais.

## FORMATO DE SAÍDA

1. [Frase completa e objetiva da deliberação.]

2. [Frase completa e objetiva da deliberação.]

## REGRA FINAL

Se não houver deliberações identificáveis com segurança, retorne exatamente:
Deliberações:
Nenhuma deliberação explícita e relevante identificada na transcrição.
""")

# ==============================================================================
# 5. VALIDADOR / CONSOLIDADOR
# ==============================================================================

PROMPT_VALIDADOR = PromptTemplate.from_template("""
Você é um revisor especializado em atas institucionais em português brasileiro.
Sua tarefa é validar e consolidar as informações geradas automaticamente, cruzando-as com a transcrição corrigida e os dados manuais.

## HIERARQUIA DE FONTES
1. Dados manuais são a fonte autoritativa para:
   - participantes;
   - nomes corretos;
   - identificação formal.
2. A transcrição corrigida é a fonte autoritativa para:
   - tópicos discutidos;
   - deliberações;
   - evidência factual do conteúdo.

## TRANSCRIÇÃO CORRIGIDA
{transcricao}

## DADOS MANUAIS
{dados_manuais}

## INFORMAÇÕES GERADAS

Participantes: {participantes}

Tópicos discutidos:
{topicos}

Deliberações:
{deliberacoes}

## REGRAS DE VALIDAÇÃO

### 1. PARTICIPANTES
- Mantenha os participantes presentes nos dados manuais.
- Corrija grafias usando os dados manuais como referência.
- Não adicione participantes novos, exceto se os dados manuais estiverem ausentes e houver evidência clara na transcrição.
- Não remova participantes constantes dos dados manuais apenas porque não falaram na transcrição.

### 2. TÓPICOS
- Mantenha apenas tópicos com evidência na transcrição.
- Remova tópicos sem evidência.
- Unifique tópicos redundantes em um único item mais completo.
- Preserve a estrutura hierárquica com subtítulos romanos e subitens.
- Não adicione tópicos novos.
- Não remova um tópico apenas porque existe uma deliberação sobre o mesmo tema, salvo se o tópico for mera repetição do encaminhamento sem contexto adicional.

### 3. DELIBERAÇÕES
- Mantenha apenas deliberações com evidência clara de encaminhamento, decisão, pendência ou próximo passo.
- Remova deliberações sem evidência ou inventadas.
- Remova deliberações redundantes.
- Remova deliberações de baixa relevância material, como comentários incidentais, preferências estéticas, microajustes cosméticos ou tarefas triviais sem impacto relevante.
- Não adicione deliberações novas.

### 4. CRUZAMENTO ENTRE TÓPICOS E DELIBERAÇÕES
Verifique se algum tópico e alguma deliberação descrevem o mesmo assunto.

- Se o tópico apenas repetir o encaminhamento já capturado na deliberação, remova o item redundante do tópico.
- Se o tópico trouxer contexto relevante que a deliberação não contém, mantenha ambos.
- Nunca remova uma deliberação válida apenas para preservar um tópico.
- Nunca esvazie artificialmente um subtítulo romano.
- Se todos os itens de um subtítulo forem removidos, remova também o subtítulo.

### 5. CONTROLE DE QUALIDADE
Antes de responder, verifique internamente:
- os participantes estão compatíveis com os dados manuais?
- todos os tópicos possuem evidência na transcrição?
- todas as deliberações possuem evidência clara na transcrição?
- alguma deliberação é irrelevante demais para constar em ata?
- há redundância real entre tópicos e deliberações?
- a estrutura hierárquica dos tópicos foi preservada?
- não há itens inventados?

### 6. TERMOS AMBÍGUOS, GÍRIAS E JARGÕES INTERNOS
- Verifique se há termos que pareçam gírias, apelidos internos, nomes improvisados de tarefas ou expressões foneticamente duvidosas.
- Só mantenha a forma literal desses termos se houver suporte claro nos dados manuais ou contexto técnico inequívoco.
- Quando o termo literal não estiver validado, mas o sentido do trecho estiver claro, substitua-o por formulação institucional semanticamente segura.
- Não preserve no texto final expressões opacas que possam induzir interpretação errada ou aparentar ser nome oficial sem evidência suficiente.                                                
                                                
## FORMATO DE SAÍDA

Retorne exclusivamente um JSON válido, sem markdown, sem aspas externas e sem explicações adicionais:

{{
  "participantes": ["Nome 1", "Nome 2"],
  "topicos": [
    "I. Subtítulo do tópico",
    "a) Item do tópico",
    "b) Item do tópico",
    "II. Subtítulo do tópico",
    "a) Item do tópico"
  ],
  "deliberacoes": [
    "Ficou definido que...",
    "Foi solicitado que..."
  ]
}}
""")