# Referência dos módulos (`scripts/`)

## `generate_docs.py`

Ponto de entrada. Orquestra análise Git → prompts → distribuição LPT → geração → escrita em disco.

| Função / símbolo | Descrição |
|------------------|-----------|
| `TASKS` | Metadados das 4 tarefas (key, path, template). |
| `read_existing(path)` | Lê Markdown existente ou placeholder. |
| `build_prompt(task, ctx, …)` | Formata o template com contexto do push. |
| `distribute_tasks(jobs, clients)` | Atribuição LPT provedor ↔ tarefa. |
| `main()` | Fluxo completo; exige `BASE_SHA` e `HEAD_SHA`. |

## `git_analyzer.py`

| Símbolo | Descrição |
|---------|-----------|
| `ChangedFile` | status (`A`/`M`/`D`/`R`), path, diff, content. |
| `PushContext` | Contexto do intervalo base→head + `diff_summary_text()`. |
| `get_push_context(base, head, max_file_chars=6000)` | Monta o contexto via comandos Git. |
| `_run(cmd)` | `subprocess.run`; em falha retorna `""`. |
| `EMPTY_TREE_SHA` | SHA da árvore vazia (primeiro push). |

## `ai_clients.py`

| Símbolo | Descrição |
|---------|-----------|
| `estimate_tokens(text)` | Heurística `max(1, len // 4)`. |
| `ClaudeClient` | `generate(prompt)` via Anthropic Messages API. |
| `GeminiClient` | `generate(prompt)` via Google GenAI. |
| `build_clients()` | Dict `{"claude"|"gemini": client}` conforme keys. |

## `prompts.py`

| Constante | Documento alvo |
|-----------|----------------|
| `BASE_CONTEXT` | Prefixo compartilhado de contexto. |
| `CHANGELOG_PROMPT` | Keep a Changelog incremental. |
| `TECHNICAL_PROMPT` | Arquitetura e módulos afetados. |
| `PARAMETRIZATION_PROMPT` | Env/flags/config em tabela. |
| `README_PROMPT` | README raiz; preserva seções não impactadas. |

Placeholders comuns: `{repo_name}`, `{module_type}`, `{module_description}`, `{folder_glossary}`, `{repo_tree}`, `{commit_messages}`, `{diff_summary}`, `{existing_content}`.

## `repo_profile.py`

| Símbolo | Descrição |
|---------|-----------|
| `IGNORED_DIR_NAMES` | Segmentos de path ignorados. |
| `FOLDER_GLOSSARY` | Descrições de pastas de negócio. |
| `MODULE_PROFILES` | Assinaturas addon / web / db / java. |
| `detect_module_type(repo_tree)` | `(chave, descrição)` por score. |
| `is_ignored_path(path)` | Filtro de ruído de build. |
| `glossary_for_paths(paths)` | Subconjunto do glossário presente no diff. |

### Glossário de pastas (resumo)

| Pasta | Significado |
|-------|-------------|
| `dashboards` | Dashboards e relatórios visuais |
| `datadictionary` | Tabelas, campos e domínios |
| `dbscripts` | Scripts DDL/DML |
| `model` | Domínio / entidades |
| `vc` | Artefatos de VC do módulo |
| `src` | Código-fonte principal |
| `functions` | Funções de negócio |
| `procedures` / `triggers` / `views` | Objetos de banco |
| `relatorios` / `sqls` / `telas` / `web` | Relatórios, SQL, UI, front-end |
