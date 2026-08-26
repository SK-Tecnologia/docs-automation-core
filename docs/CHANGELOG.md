# Changelog

Todas as mudanças notáveis deste projeto são documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Unreleased]

## [0.1.0] - 2026-08-26

### Added

- Orquestrador `scripts/generate_docs.py` com distribuição LPT entre Claude e Gemini.
- Análise de push em `scripts/git_analyzer.py` (diff, árvore, mensagens de commit).
- Clientes Anthropic e Google GenAI em `scripts/ai_clients.py`.
- Templates de prompt para CHANGELOG, TECHNICAL, PARAMETRIZATION e README.
- Perfil de repositórios Sankhya em `scripts/repo_profile.py` (glossário, ignore list, detecção addon/web/db/java).
- Documentação do núcleo: README, TECHNICAL, PARAMETRIZATION, MODULES.
- `requirements.txt` com `anthropic` e `google-genai`.
