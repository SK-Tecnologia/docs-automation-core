"""
Orquestrador da documentação automática.

Fluxo:
1. Lê o diff do push atual (BASE_SHA -> HEAD_SHA).
2. Monta 4 "tarefas" de documentação (changelog, técnico, parametrização, README).
3. Estima o tamanho (tokens) de cada tarefa e distribui entre Claude e Gemini
   usando um algoritmo guloso (LPT - Longest Processing Time first), que
   equilibra a carga total entre as duas IAs, e não fixa "doc X = IA Y".
4. Chama cada IA e grava o resultado no arquivo correspondente.
"""

import os
import sys
from pathlib import Path

from git_analyzer import get_push_context
from ai_clients import build_clients, estimate_tokens
from repo_profile import glossary_for_paths, detect_module_type
import prompts

# IMPORTANTE: com o modelo de "repo central" (reusable workflow), este
# script roda a partir de scripts/ dentro do repo central, mas precisa
# escrever nos arquivos do repo ALVO (o que disparou o push). Por isso
# usamos o diretório de trabalho atual (definido pelo workflow como a raiz
# do checkout do repo alvo) em vez de derivar o caminho a partir de __file__.
REPO_ROOT = Path.cwd()
DOCS_DIR = REPO_ROOT / "docs"

# Cada tarefa: nome, caminho do arquivo final, template de prompt
TASKS = [
    {"key": "changelog", "path": DOCS_DIR / "CHANGELOG.md", "template": prompts.CHANGELOG_PROMPT},
    {"key": "technical", "path": DOCS_DIR / "TECHNICAL.md", "template": prompts.TECHNICAL_PROMPT},
    {"key": "parametrization", "path": DOCS_DIR / "PARAMETRIZATION.md", "template": prompts.PARAMETRIZATION_PROMPT},
    {"key": "readme", "path": REPO_ROOT / "README.md", "template": prompts.README_PROMPT},
]


def read_existing(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else "(arquivo ainda não existe)"


def build_prompt(task: dict, ctx, module_type: str, module_description: str) -> str:
    changed_paths = [f.path for f in ctx.changed_files]
    return task["template"].format(
        repo_name=os.environ.get("REPO_NAME", "repositório"),
        module_type=module_type,
        module_description=module_description,
        folder_glossary=glossary_for_paths(changed_paths),
        repo_tree=ctx.repo_tree[:4000],
        commit_messages="\n".join(f"- {m}" for m in ctx.commit_messages) or "(sem mensagens de commit novas)",
        diff_summary=ctx.diff_summary_text()[:12000],
        existing_content=read_existing(task["path"])[:4000],
    )


def distribute_tasks(jobs: list[dict], clients: dict) -> dict:
    """Bin-packing guloso (LPT): ordena as tarefas da maior pra menor em tokens
    estimados e vai atribuindo sempre à IA que está com menos carga acumulada.
    Se só houver uma API key configurada, tudo vai pra ela automaticamente."""
    provider_names = list(clients.keys())
    load = {p: 0 for p in provider_names}
    assignment = {}

    jobs_sorted = sorted(jobs, key=lambda j: j["tokens"], reverse=True)
    for job in jobs_sorted:
        chosen = min(provider_names, key=lambda p: load[p])
        assignment[job["key"]] = chosen
        load[chosen] += job["tokens"]

    print("== Distribuição de tarefas ==")
    for job in jobs_sorted:
        print(f"  {job['key']:16s} -> {assignment[job['key']]:8s} (~{job['tokens']} tokens)")
    print(f"  Carga total estimada por IA: {load}")

    return assignment


def main():
    base_sha = os.environ["BASE_SHA"]
    head_sha = os.environ["HEAD_SHA"]

    ctx = get_push_context(base_sha, head_sha)
    if not ctx.changed_files:
        print("Nenhum arquivo relevante alterado neste push. Encerrando sem gerar docs.")
        return

    clients = build_clients()

    module_type, module_description = detect_module_type(ctx.repo_tree)
    print(f"Tipo de módulo detectado: {module_type} — {module_description}")

    # Monta as tarefas com prompt já pronto + estimativa de tokens
    jobs = []
    for task in TASKS:
        prompt = build_prompt(task, ctx, module_type, module_description)
        jobs.append({**task, "prompt": prompt, "tokens": estimate_tokens(prompt)})

    assignment = distribute_tasks(jobs, clients)

    DOCS_DIR.mkdir(exist_ok=True)

    for job in jobs:
        provider = assignment[job["key"]]
        client = clients[provider]
        print(f"Gerando '{job['key']}' com {provider}...")
        try:
            content = client.generate(job["prompt"])
        except Exception as e:
            print(f"  ERRO ao gerar '{job['key']}' com {provider}: {e}", file=sys.stderr)
            continue
        job["path"].write_text(content.strip() + "\n", encoding="utf-8")
        print(f"  OK -> {job['path'].relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
