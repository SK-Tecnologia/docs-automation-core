# Parametrização — docs-automation-core

## Variáveis de ambiente

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|--------|-----------|
| `BASE_SHA` | string (SHA) | sim | — | Commit base do push. Se vazio ou só `0`, usa a empty tree do Git. |
| `HEAD_SHA` | string (SHA) | sim | — | Commit HEAD do push analisado. |
| `REPO_NAME` | string | não | `repositório` | Nome injetado nos prompts. |
| `ANTHROPIC_API_KEY` | string | condicional* | — | Habilita o cliente Claude. |
| `GEMINI_API_KEY` | string | condicional* | — | Habilita o cliente Gemini. |

\* Pelo menos uma das duas API keys deve estar definida.

## Modelos de IA

| Cliente | Parâmetro de construção | Valor padrão | Observação |
|---------|-------------------------|--------------|------------|
| Claude | `model` | `claude-sonnet-5` | Definido em `ClaudeClient.__init__` |
| Gemini | `model` | `gemini-2.5-flash` | Definido em `GeminiClient.__init__` |
| Ambos | `max_tokens` em `generate` | `8000` | Limite de saída por chamada |

Para trocar o modelo, altere o default (ou passe o argumento) em `scripts/ai_clients.py`.

## Limites e truncamentos

| Parâmetro | Onde | Padrão | Efeito |
|-----------|------|--------|--------|
| `max_file_chars` | `get_push_context` | `6000` | Teto de chars por diff e por conteúdo de arquivo. |
| Árvore no prompt | `build_prompt` | `4000` | `ctx.repo_tree[:4000]` |
| Diff no prompt | `build_prompt` | `12000` | `diff_summary_text()[:12000]` |
| Doc existente | `build_prompt` | `4000` | Conteúdo atual do arquivo alvo. |
| Estimativa de tokens | `estimate_tokens` | `len // 4` | Usada só para balancear carga (não é billing). |

## Pastas e arquivos ignorados

Segmentos de caminho (case-insensitive) em `IGNORED_DIR_NAMES`:

`.gradle`, `.idea`, `.run`, `.vscode`, `.git`, `build`, `gradle`, `out`, `libs`, `node_modules`, `dist`, `target`, `.venv`, `__pycache__`

Arquivos sob essas pastas não entram em `changed_files` nem em `repo_tree`.

## Saídas geradas (no repositório alvo)

| Arquivo | Criado se não existir |
|---------|------------------------|
| `docs/` | sim (`mkdir`) |
| `docs/CHANGELOG.md` | sobrescrito após geração |
| `docs/TECHNICAL.md` | sobrescrito após geração |
| `docs/PARAMETRIZATION.md` | sobrescrito após geração |
| `README.md` | sobrescrito após geração |

## Dependências Python

Ver `requirements.txt`:

| Pacote | Uso |
|--------|-----|
| `anthropic>=0.40.0` | API Claude |
| `google-genai>=1.0.0` | API Gemini |

## Exemplo mínimo (local)

```bash
export BASE_SHA=4b825dc642cb6eb9a060e54bf8d69288fbee4904
export HEAD_SHA=$(git rev-parse HEAD)
export REPO_NAME=meu-modulo
export GEMINI_API_KEY=sua_chave

pip install -r requirements.txt
python scripts/generate_docs.py
```

> Execute a partir da raiz do repositório que deve receber os arquivos gerados.
