"""
Templates de prompt para cada documento gerado.
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
Tarefa: gerar um arquivo de alteração (changelog) apenas para ESTE push.

Contexto (o arquivo de destino ainda não existe; ignore histórico antigo):
{existing_content}

Instruções:
- Gere somente o conteúdo desta alteração (não mescle histórico de outros arquivos).
- Siga o padrão "Keep a Changelog" (Added / Changed / Fixed / Removed) quando aplicável.
- Use a data/hora de hoje no título da entrada.
- Resuma o que mudou neste push com base nos commits e diffs acima (não invente funcionalidades).
- Responda APENAS com o Markdown final do arquivo, sem comentários extras.
"""


TECHNICAL_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar a documentação técnica do projeto (docs/technical/tecnica.md).

Conteúdo atual de docs/technical/tecnica.md (pode estar vazio):
{existing_content}

Instruções:
- Descreva arquitetura, principais módulos/classes/funções afetados pelas mudanças,
  decisões de design relevantes e como os componentes se relacionam.
- Atualize apenas as seções afetadas pelas mudanças deste push; preserve o restante do documento.
- Use linguagem técnica, objetiva, com exemplos de código quando fizer sentido.
- Responda APENAS com o conteúdo final completo do arquivo em Markdown.
"""


PARAMETRIZATION_PROMPT = BASE_CONTEXT + """
Tarefa: gerar/atualizar a documentação de parametrização (docs/configuration/parametrizacao.md).

Conteúdo atual de docs/configuration/parametrizacao.md (pode estar vazio):
{existing_content}

Instruções:
- Liste variáveis de ambiente, arquivos de configuração, flags de linha de comando,
  parâmetros de funções públicas/endpoints e valores padrão que foram adicionados,
  alterados ou removidos neste push.
- Formate como tabela Markdown quando possível (Parâmetro | Tipo | Padrão | Descrição).
- Preserve parametrizações antigas não afetadas por este push.
- Responda APENAS com o conteúdo final completo do arquivo em Markdown.
"""
