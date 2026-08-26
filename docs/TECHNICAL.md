# Documentação técnica — docs-automation-core

## Visão geral

O núcleo transforma o contexto de um **push Git** (diff + árvore + mensagens de commit) em quatro documentos Markdown, usando uma ou duas IAs de forma intercambiável.

```
BASE_SHA / HEAD_SHA
        │
        ▼
┌───────────────────┐
│  git_analyzer     │  → PushContext (arquivos, diffs, árvore, commits)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  repo_profile     │  → tipo de módulo + glossário das pastas alteradas
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  prompts          │  → 4 prompts formatados (changelog, técnico, params, README)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  distribute_tasks │  → LPT: maior prompt → IA com menor carga acumulada
│  (generate_docs)  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  ai_clients       │  → ClaudeClient / GeminiClient (.generate)
└─────────┬─────────┘
          │
          ▼
   arquivos Markdown no repo alvo
```

## Modelo de execução (repo central)

Os scripts vivem neste repositório central, mas **escrevem no working directory atual** (`Path.cwd()`), não relativos a `__file__`. Isso permite que um reusable workflow:

1. Faça checkout do repositório alvo
2. Disponibilize `scripts/` deste core
3. Execute `generate_docs.py` com CWD = raiz do alvo

Assim, `docs/CHANGELOG.md`, `docs/TECHNICAL.md`, `docs/PARAMETRIZATION.md` e `README.md` são atualizados no projeto que disparou o push.

## Componentes

### `generate_docs.py`

Orquestrador. Responsabilidades:

- Ler `BASE_SHA` e `HEAD_SHA` do ambiente
- Obter `PushContext` via `get_push_context`
- Encerrar cedo se não houver arquivos relevantes alterados
- Detectar tipo de módulo e montar prompts
- Estimar tokens (`len(texto) // 4`) e distribuir tarefas (LPT)
- Chamar a IA atribuída e gravar o arquivo correspondente

**Lista de tarefas fixa:**

| key | destino no repo alvo | template |
|-----|----------------------|----------|
| `changelog` | `docs/CHANGELOG.md` | `CHANGELOG_PROMPT` |
| `technical` | `docs/TECHNICAL.md` | `TECHNICAL_PROMPT` |
| `parametrization` | `docs/PARAMETRIZATION.md` | `PARAMETRIZATION_PROMPT` |
| `readme` | `README.md` | `README_PROMPT` |

Truncamentos aplicados ao montar o prompt:

- árvore do repo: 4000 caracteres
- resumo de diffs: 12000 caracteres
- conteúdo existente do doc: 4000 caracteres

Erros por tarefa são logados em stderr; as demais tarefas seguem.

### `git_analyzer.py`

Constrói `PushContext`:

| Campo | Origem |
|-------|--------|
| `changed_files` | `git diff --name-status` + diff unificado + `git show` |
| `repo_tree` | `git ls-tree -r --name-only` (filtrado) |
| `commit_messages` | `git log base..head --pretty=format:%s` |

Comportamentos importantes:

- Se `BASE_SHA` for vazio ou só zeros (primeiro push), usa a empty tree SHA do Git (`4b825dc…`).
- Diff e conteúdo por arquivo limitados a `max_file_chars` (padrão 6000).
- Falhas de subprocessos Git retornam string vazia (não derrubam o workflow).
- Caminhos filtrados por `is_ignored_path` (build/IDE).

### `ai_clients.py`

Interface comum: `generate(prompt: str) -> str`.

| Classe | SDK | Modelo padrão | Env |
|--------|-----|---------------|-----|
| `ClaudeClient` | `anthropic` | `claude-sonnet-5` | `ANTHROPIC_API_KEY` |
| `GeminiClient` | `google.genai` | `gemini-3.6-flash` | `GEMINI_API_KEY` |

`build_clients()` instancia só as IAs com key presente. Se nenhuma key existir, lança `RuntimeError`.

### `prompts.py`

`BASE_CONTEXT` compartilha: nome do repo, tipo de módulo, glossário de pastas, árvore, commits e diffs. Cada prompt especializa a tarefa (Keep a Changelog, arquitetura, tabelas de parâmetros, README) e pede **apenas** o Markdown final.

### `repo_profile.py`

Conhecimento fixo do padrão Sankhya:

- `IGNORED_DIR_NAMES` — ruído de build/tooling
- `FOLDER_GLOSSARY` — significado de pastas de negócio (`dashboards`, `model`, `telas`, …)
- `MODULE_PROFILES` — assinaturas para score de detecção (`addon` / `web` / `db` / `java`)

`detect_module_type` pontua sobreposição de pastas de topo e nomes de arquivo; score 0 → `desconhecido`.

## Algoritmo de distribuição (LPT)

1. Ordenar jobs por tokens estimados (maior → menor)
2. Atribuir cada job ao provedor com menor carga acumulada
3. Se só houver um provedor, todas as tarefas vão para ele

Objetivo: equilibrar custo/latência entre Claude e Gemini sem fixar “doc X = IA Y”.

## Extensão

- Novos documentos: entrada em `TASKS` + template em `prompts.py`
- Novas pastas de glossário: chave em `FOLDER_GLOSSARY`
- Novo tipo de módulo: perfil em `MODULE_PROFILES`
- Outro provedor de IA: classe com `.generate` + registro em `build_clients`
