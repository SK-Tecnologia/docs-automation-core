"""
Analisa o que mudou no push atual: arquivos alterados, diffs unificados
e uma foto da árvore do repositório para dar contexto às IAs.
"""

import subprocess
from dataclasses import dataclass, field

from repo_profile import is_ignored_path

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # árvore vazia do git


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # não derruba o workflow por causa de um comando git específico
        return ""
    return result.stdout


@dataclass
class ChangedFile:
    status: str        # A (added) / M (modified) / D (deleted) / R (renamed)
    path: str
    diff: str = ""
    content: str = ""  # conteúdo atual do arquivo (para A/M), truncado se necessário


@dataclass
class PushContext:
    base_sha: str
    head_sha: str
    changed_files: list[ChangedFile] = field(default_factory=list)
    repo_tree: str = ""
    commit_messages: list[str] = field(default_factory=list)

    def diff_summary_text(self) -> str:
        """Resumo textual compacto de todas as mudanças, usado nos prompts."""
        parts = []
        for f in self.changed_files:
            parts.append(f"### [{f.status}] {f.path}")
            if f.diff:
                parts.append(f.diff)
        return "\n".join(parts)


def get_push_context(base_sha: str, head_sha: str, max_file_chars: int = 6000) -> PushContext:
    # Primeiro push na branch: base_sha vem zerado (todos '0')
    if not base_sha or set(base_sha) == {"0"}:
        base_sha = EMPTY_TREE_SHA

    ctx = PushContext(base_sha=base_sha, head_sha=head_sha)

    # Lista de arquivos alterados com status
    name_status = _run(["git", "diff", "--name-status", base_sha, head_sha])
    for line in name_status.splitlines():
        if not line.strip():
            continue
        cols = line.split("\t")
        status, path = cols[0], cols[-1]

        # Ignora ruído de build/IDE (.gradle, .idea, build, out, libs, node_modules...)
        # independente de qual repositório (addon/web/core) estiver rodando.
        if is_ignored_path(path):
            continue

        cf = ChangedFile(status=status[0], path=path)

        # diff unificado por arquivo (limitado, só o essencial)
        cf.diff = _run(["git", "diff", base_sha, head_sha, "--", path])[:max_file_chars]

        # conteúdo atual do arquivo (para dar contexto completo, não só o diff)
        if status[0] in ("A", "M", "R"):
            content = _run(["git", "show", f"{head_sha}:{path}"])
            cf.content = content[:max_file_chars]

        ctx.changed_files.append(cf)

    # Árvore geral do repositório (ajuda a IA a entender o padrão do projeto),
    # também sem ruído de build/tooling.
    full_tree = _run(["git", "ls-tree", "-r", "--name-only", head_sha])
    ctx.repo_tree = "\n".join(
        line for line in full_tree.splitlines() if not is_ignored_path(line)
    )

    # Mensagens de commit do intervalo (úteis pro changelog)
    log = _run(["git", "log", f"{base_sha}..{head_sha}", "--pretty=format:%s"])
    ctx.commit_messages = [l for l in log.splitlines() if l.strip()]

    return ctx
