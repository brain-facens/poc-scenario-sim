# Brain Hub API (Proof of Concept – Scenario Sim) 🧠

O **Brain Hub API** é um back-end robusto e modular construído em **FastAPI**, servindo como infraestrutura central para provas de conceito (PoCs) e sistemas focados em Inteligência Artificial, transcrição acelerada por GPU e pipelines orquestrados de Agentes LLM.

## 🌟 Principais Módulos da Aplicação

### 1. Gerador de Atas Autônomo (`gerador_atas`)
A "joia da coroa" atual do repositório. Este módulo não apenas transcreve áudios com alta precisão, mas orquestra um enxame de agentes LLMs paralelos para formular a documentação executiva (DOCX) instantaneamente.

**Arquitetura e Highlights:**
* **WhisperX com Lock na VRAM e Coleta de Lixo Ativa:** Carregamento em padrão _Singleton_ isolado (`Semaphore(1)`) do pipeline de Transcrição + Diarização atuando via PyTorch (CUDA). Possui varredura de fragmentação (`gc.collect`) garantindo que Placas de Vídeo (GPU) de uso comum comercial (com 4GB a 8GB de memória) processem múltiplos arquivos sem o erro letal de _Cuda Out-Of-Memory (OOM)_.
* **Viabilidade na CPU e Configuração Dinâmica:** Flexibilidade nativa para desenvolvedores. As dimensões dos Modelos (`turbo`, `small`, etc) são parametrizáveis pelo `.env`. Se executado em um servidor virtual de baixo custo sem GPU na nuvem, o sistema migra puramente para os núcleos do processador (CPU) preservando a aplicação em pé em _graceful degradation_.
* **Smart LLM Routing (Cascata Dinâmica):** É possível trabalhar integralmente local (`Ollama` atuando em rede via KV Cache) ou acionar o motor `OpenAI` nativo usufruindo da técnica de **Prompt Caching** (injeção otimizada para corte de 80% dos custos e diminuição extrema de latência). O sistema faz fallback automático caso os créditos da nuvem se esgotem.
* **Master Flow Paralelo:** Sem fila indiana de agentes. Introdução, Tópicos e Deliberações são forjados rodando simultaneamente (`asyncio.gather`), despejando Markdowns diretos para dentro da lógica nativa em listagem de Python. Transformação `Audio -> LLM Paralelo -> Arquivo Word (.docx)` com zero burocracia de tempo.

### 2. Scenario Simulator (`scenario_sim`)
Módulo core nativo que dá o título da PoC, focado na orquestração, manipulação e gerenciamento de simulação de cenários complexos de Inteligência Artificial usando lógica relacional (SQLAlchemy) associada com outputs de inferência.

**Arquitetura e Highlights:**
* **Motor Baseado em Regras e Inferência:** Integração robusta com Agentes LLM para avaliar cenários, interpretar consequências e simular ramificações imprevisíveis de negócio.
* **Tração e Persistência Dinâmica do Contexto:** O estado das simulações é altamente rastreável. Cada interação e desdobramento é mapeado e versionado usando ORM assíncrono para replays ou derivações de contexto.

### 3. Voice Changer (`voice_changer`)
Tratamento e mutação de amostras vocais para fluxos de processamento baseados em Inteligências Artificiais e modelos locais de áudio generativo.

**Arquitetura e Highlights:**
* **Processamento Acústico GenAI:** Camada voltada para carregar e pré-processar streams de voz, transmutando timbres via modelos difusores e geradores acústicos.
* **Stream e I/O Assíncrono:** Desenvolvido prevendo inputs binários e chunks de áudio via web sem bloquear o Worker do FastAPI, escalando para recepções simultâneas.

### 4. Auth & Security (`auth`)
Gerenciamento de identidades, senhas com salt (`passlib[argon2]`), chaves simétricas providas por JWT e validações em cascata para as rotas seguras do FastAPI.

**Arquitetura e Highlights:**
* **Criptografia Argon2:** Hashing de vanguarda que barra ataques volumétricos (como Rainbow Tables e Brute-force via GPU), exigindo sacrifício alto e lento de hardware para derivação das chaves.
* **Sessão Stateless Multi-Nó (JWT):** Sem sobrecarga de State em Banco de Dados. A API escala horizontalmente com facilidade, resolvendo permissões inteiramente nas portas rotineiras do pacote `Depends` do FastAPI.

---

## 🛠 Tech Stack

- **Framework Web:** FastAPI + Uvicorn
- **Banco de Dados:** SQLAlchemy (ORM) + Alembic (Migrations)
- **Engine LLM:** OpenAI API + LangChain Core + Ollama API (fallback configurável)
- **Processamento Acústico/CUDA:** Torch, Numpy, OpenAI-Whisper, WhisperX
- **Segurança:** Python-Jose (JWT), Passlib
- **Docs:** WeasyPrint + Python DOCX nativos

---

## 🚀 Como Executar Localmente

### 1. Pré-Requisitos

- **Python 3.12+**
- (Opcional, mas exigido para transcrições e processamentos locais espessos) **Placa de Vídeo NVIDIA** (CUDA 11.8+ / 12.0+) 

> [!IMPORTANT]
> **Atenção (Diarização):** Para que a separação de vozes (Speaker Diarization) funcione, você **PRECISA** aceitar os termos de uso dos seguintes modelos no Hugging Face com sua conta logada, e depois gerar um `HF_KEY` (Read Token):
> 1. [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
> 2. [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

### 2. Instalação e Ambiente Virtual

Para isolar as dependências apropriadamente de forma limpa, inicialize o ambiente através do **Conda**:

```bash
conda create -n qa python==3.11.14
conda activate qa
cd poc-scenario-sim
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto puxando do `.env.example`:
```bash
# Definindo as chaves (OpenAI e Hugging Face)
OPENAI_KEY="sk-..."
HF_KEY="hf_..."

# Configurando o fallback da Engine das LLMs
# 'auto': Tenta OpenAI para paralelismo veloz com Prompt Caching, e recua pro Ollama se falhar
# 'local': Força o uso do Ollama e desabilita requests pra web
BACKEND_MODE="auto" 

# Configuração da Transcrição e Gestão de VRAM
# 'local': Vai utilizar a Placa de Vídeo / Processador Local
TRANSCRIBE_BACKEND="local" 
# Gestões de perfomance p/ evitar Gargalos (Leia os topicos do README)
WHISPER_MODEL_SIZE="small" 
WHISPER_COMPUTE_TYPE="int8"
WHISPER_BATCH_SIZE="1" 
```

### 4. Banco de Dados
Aqueça o banco de dados rodando a cabeça das migrations do Alembic:
```bash
cd src
alembic upgrade head
```

### 5. Start na Aplicação
Navegue até a raiz do `src/` e suba o servidor usando Uvicorn:
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Acesse o Painel do **Swagger UI** (Swagger Docs) p/ testes de rotas: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔄 Migrações e Reset do Banco (Desenvolvimento)

Como o projeto está em fase inicial de **Proof of Concept (PoC)** e a estrutura das tabelas é altamente volátil, não estamos utilizando fluxos complexos de migração incremental para não travar a agilidade do desenvolvimento.

Para realizar uma migração limpa em ambiente de **DESENVOLVIMENTO**, siga estes passos:

1.  **Limpeza de Versões:** Vá até a pasta raiz e delete todos os arquivos dentro de `alembic/versions/` (mantenha apenas a pasta e o arquivo `script.py.mako` se houver).
2.  **Reset do Banco:** Delete o arquivo atual do banco de dados (ex: `.db`) que reside dentro da pasta `src/`.
3.  **Gerar Nova Revisão:** Execute o comando para mapear a estrutura atual:
    ```bash
    alembic revision --autogenerate -m "init db"
    ```
4.  **Aplicar Migração:** Suba a nova estrutura para o banco:
    ```bash
    alembic upgrade head
    ```

> ⚠️ **Nota:** Este procedimento apaga todos os dados locais. Use apenas enquanto a estrutura do banco estiver mudando drasticamente dia após dia.

---

## 📂 Estrutura de Diretórios Básica

```
poc-scenario-sim/
│
├── alembic/                 # Versões e migrações do Banco de Dados
├── src/
│   ├── core/                # Setup global, paginações, configurações de App
│   ├── modules/
│   │   ├── auth/            # JWT, Login, Passwords
│   │   ├── gerador_atas/    # Pipeline do Flow do WhisperX + Agentes Paralelos LLM
│   │   ├── scenario_sim/    # Lógica de negócio de simulações
│   │   ├── voice_changer/   # Tratamento de mutações acústicas
│   │   └── logging/         # Handlers de histórico de erros e reports
│   └── main.py              # Ponto de entrada p/ montar os routers do FastAPI
│
├── requirements.txt         # Pacotes Python
├── .env.example             # Template das envvars da aplicação
└── README.md
```

👨‍💻 _Mantido pela equipe interna – BRAIN._