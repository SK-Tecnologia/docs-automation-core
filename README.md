# docs-automation-core

Núcleo reutilizável de **documentação automática por IA** para repositórios Sankhya (addon, web, db, java). Em cada push, analisa o diff do Git, detecta o tipo de módulo e gera/atualiza:

| Artefato | Caminho |
|----------|---------|
| Changelog (por alteração) | `docs/changelog/alteracao_<timestamp>.md` |
| Documentação técnica | `docs/technical/tecnica.md` |
| Parametrização | `docs/configuration/parametrizacao.md` |

As tarefas são distribuídas entre **Claude** (Anthropic) e **Gemini** (Google) com balanceamento guloso por tokens estimados (LPT — *Longest Processing Time first*).

## Requisitos

- Python 3.10+
- Git
- Pelo menos uma API key: `ANTHROPIC_API_KEY` e/ou `GEMINI_API_KEY`

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

O orquestrador espera rodar na **raiz do repositório alvo** (checkout do workflow), com as variáveis de ambiente abaixo definidas:

```bash
export BASE_SHA=<sha_antes_do_push>   # ou zeros no primeiro push
export HEAD_SHA=<sha_atual>
export REPO_NAME=<nome_do_repositorio>  # opcional

export ANTHROPIC_API_KEY=...   # opcional se Gemini estiver configurado
export GEMINI_API_KEY=...      # opcional se Claude estiver configurado

cd /caminho/do/repo/alvo
python /caminho/docs-automation-core/scripts/generate_docs.py
```

Em GitHub Actions, este repositório costuma ser consumido como **reusable workflow**: o job faz checkout do repo alvo, clona/copia estes scripts e os executa no working directory do alvo.

Workflows reutilizáveis disponíveis:

| Workflow | Uso |
|----------|-----|
| `reusable-auto-docs.yml` | Gera documentação em push |
| `reusable-release.yml` | Cria tag `v*` e GitHub Release |

## Estrutura

```
docs-automation-core/
├── README.md
├── requirements.txt
├── docs/                 # documentação deste núcleo
│   ├── CHANGELOG.md
│   ├── TECHNICAL.md
│   ├── PARAMETRIZATION.md
│   └── MODULES.md
└── scripts/
    ├── generate_docs.py  # orquestrador
    ├── git_analyzer.py   # diff / árvore / commits do push
    ├── ai_clients.py     # Claude + Gemini
    ├── prompts.py        # templates dos 4 documentos
    └── repo_profile.py   # glossário de pastas e detecção de módulo
```

## Documentação

- [Documentação técnica](docs/TECHNICAL.md) — arquitetura e fluxo
- [Parametrização](docs/PARAMETRIZATION.md) — variáveis, modelos e limites
- [Módulos](docs/MODULES.md) — referência por script
- [Changelog](docs/CHANGELOG.md)

## Tipos de módulo detectados

| Tipo | Assinatura típica |
|------|-------------------|
| `addon` | `build.gradle`, pastas `model` / `vc` |
| `web` | `index.jsp`, `index.html.ejs`, `package.json.ejs` |
| `db` | `procedures`, `triggers`, `views`, `sqls`, `dbscripts` |
| `java` | pastas `libs` / `out` |

Pastas de build/IDE (`.gradle`, `build`, `node_modules`, etc.) são ignoradas na análise.

## Licença

Uso interno Sankhya.
