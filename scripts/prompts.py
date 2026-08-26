"""
Templates de prompt para cada um dos 4 documentos.
Ajuste o tom/idioma/seções conforme o padrão real do seu projeto.
"""

BASE_CONTEXT = """Você é um assistente técnico que documenta um repositório de software.
Nome do repositório: {repo_name}

Tipo de módulo detectado automaticamente: {module_type} — {module_description}

Este repositório segue um padrão de pastas conhecido. Glossário das pastas
de conteúdo (não-build) alteradas neste push:
{folder_glossary}

Estrutura atual do repositório (arquivos rastreados pelo git, sem artefatos de build):
{repo_tree}

Commits incluídos neste push:
{commit_messages}

Arquivos alterados neste push e seus diffs:
{diff_summary}
"""


CHANGELOG_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar o CHANGELOG.md do projeto.

Conteúdo atual do CHANGELOG.md (pode estar vazio se for a primeira geração):
{existing_content}

Instruções:
- Siga o padrão "Keep a Changelog" (Added / Changed / Fixed / Removed).
- Adicione uma NOVA entrada no topo, com a data de hoje, resumindo o que mudou neste push
  com base nos commits e diffs acima (não invente funcionalidades que não estão no diff).
- Mantenha todo o histórico anterior abaixo, sem reescrevê-lo.
- Responda APENAS com o conteúdo final completo do arquivo CHANGELOG.md, em Markdown, sem comentários extras.
"""


TECHNICAL_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar a documentação técnica do projeto (docs/TECHNICAL.md).

Conteúdo atual de docs/TECHNICAL.md (pode estar vazio):
{existing_content}

Instruções:
- Descreva arquitetura, principais módulos/classes/funções afetados pelas mudanças,
  decisões de design relevantes e como os componentes se relacionam.
- Atualize apenas as seções afetadas pelas mudanças deste push; preserve o restante do documento.
- Use linguagem técnica, objetiva, com exemplos de código quando fizer sentido.
- Responda APENAS com o conteúdo final completo do arquivo em Markdown.
"""


PARAMETRIZATION_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar a documentação de parametrização (docs/PARAMETRIZATION.md).

Conteúdo atual de docs/PARAMETRIZATION.md (pode estar vazio):
{existing_content}

Instruções:
- Liste variáveis de ambiente, arquivos de configuração, flags de linha de comando,
  parâmetros de funções públicas/endpoints e valores padrão que foram adicionados,
  alterados ou removidos neste push.
- Formate como tabela Markdown quando possível (Parâmetro | Tipo | Padrão | Descrição).
- Preserve parametrizações antigas não afetadas por este push.
- Responda APENAS com o conteúdo final completo do arquivo em Markdown.
"""


README_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar o README.md principal do projeto (raiz do repositório).

Conteúdo atual do README.md (pode estar vazio):
{existing_content}

Instruções:
- Atualize descrição do projeto, instalação, uso e exemplos se as mudanças deste push impactarem
  essas seções (ex.: nova dependência, novo comando, nova pasta relevante).
- Não remova seções existentes que não foram impactadas.
- Se nada relevante para o README mudou, apenas devolva o conteúdo atual sem alterações.
- Responda APENAS com o conteúdo final completo do arquivo em Markdown.
"""
