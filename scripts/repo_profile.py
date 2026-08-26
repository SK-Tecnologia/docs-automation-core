"""
Conhecimento fixo sobre o PADRÃO de pastas usado nos seus repositórios
(addon, web, core, etc). Isso permite que o script já saiba, sem
configuração extra por repo, o que é ruído de build/tooling e o que é
conteúdo de negócio relevante pra documentação.

Casa por nome de pasta em qualquer nível do caminho, case-insensitive,
então funciona tanto pra "dashboards" quanto "Dashboards", "SRC/Dashboards"
etc, independente de qual dos repositórios (addon / web / core) estiver
rodando o workflow.
"""

# Pastas de build/IDE/artefato: nunca entram na análise, mesmo que mudem.
IGNORED_DIR_NAMES = {
    ".gradle", ".idea", ".run", ".vscode", ".git",
    "build", "gradle", "out", "libs", "node_modules",
    "dist", "target", ".venv", "__pycache__",
}

# Descrição de cada pasta de conteúdo conhecida, injetada no prompt como
# contexto sempre que a pasta aparecer no diff. Ajuste os textos livremente
# conforme o significado real no seu padrão de projeto.
FOLDER_GLOSSARY = {
    "dashboards": "Definições/artefatos de dashboards e relatórios visuais.",
    "datadictionary": "Dicionário de dados: definição de tabelas, campos e domínios.",
    "dbscripts": "Scripts de banco de dados (DDL/DML) versionados do módulo.",
    "model": "Camada de modelo/domínio da aplicação (entidades, regras).",
    "vc": "Configurações ou artefatos de controle de versão específicos do módulo.",
    "src": "Código-fonte principal do módulo.",
    "functions": "Funções de negócio reutilizáveis.",
    "procedures": "Stored procedures de banco de dados.",
    "relatorios": "Relatórios do sistema (definição/layout/consulta).",
    "sqls": "Consultas SQL avulsas usadas pela aplicação.",
    "telas": "Componentes/definições de telas (UI).",
    "triggers": "Triggers de banco de dados.",
    "views": "Views de banco de dados.",
    "web": "Camada web/front-end do módulo.",
}


# Os 4 tipos de repositório/módulo que você usa. Cada repo é sempre UM
# desses tipos (não uma mistura). A detecção é automática, por assinatura
# de arquivos/pastas típicas de cada tipo — não precisa configurar nada
# manualmente por repositório.
MODULE_PROFILES = {
    "addon": {
        "label": "Addon (Java/Gradle)",
        "description": (
            "Módulo Java/Gradle: integrações e regras de negócio backend. "
            "Build gerenciado via Gradle (build.gradle)."
        ),
        "signature_files": {"build.gradle"},
        "signature_dirs": {"model", "vc", ".gradle"},
    },
    "web": {
        "label": "Web (JSP/Front-end)",
        "description": (
            "Módulo Web: camada de apresentação/front-end, telas JSP/HTML e "
            "empacotamento via package.json.ejs."
        ),
        "signature_files": {"index.jsp", "index.html.ejs", "package.json.ejs"},
        "signature_dirs": set(),
    },
    "db": {
        "label": "DB (Banco de dados)",
        "description": (
            "Módulo de banco de dados: procedures, triggers, views e scripts SQL "
            "que definem a camada de dados do sistema."
        ),
        "signature_files": set(),
        "signature_dirs": {"procedures", "triggers", "views", "sqls", "dbscripts"},
    },
    "java": {
        "label": "Java (biblioteca/serviço)",
        "description": (
            "Módulo Java compilado fora do padrão Gradle do addon (ex.: libs "
            "externas em libs/, saída em out/)."
        ),
        "signature_files": set(),
        "signature_dirs": {"libs", "out"},
    },
}


def detect_module_type(repo_tree: str) -> tuple[str, str]:
    """Detecta automaticamente o tipo de módulo (addon/web/db/java) a partir
    da árvore de arquivos do HEAD, comparando com as assinaturas conhecidas.
    Retorna (chave_do_tipo, descrição) — usa 'desconhecido' se nada bater."""
    paths = repo_tree.splitlines()
    top_dirs = {p.split("/")[0].lower() for p in paths if "/" in p}
    file_names = {p.split("/")[-1].lower() for p in paths}

    scores = {}
    for key, profile in MODULE_PROFILES.items():
        score = 0
        score += len(profile["signature_dirs"] & top_dirs)
        score += len({f.lower() for f in profile["signature_files"]} & file_names)
        scores[key] = score

    best_key = max(scores, key=scores.get)
    if scores[best_key] == 0:
        return "desconhecido", "Tipo de módulo não identificado automaticamente."
    return best_key, MODULE_PROFILES[best_key]["description"]


def is_ignored_path(path: str) -> bool:
    """True se qualquer segmento do caminho for uma pasta de build/tooling."""
    segments = {seg.lower() for seg in path.split("/")}
    return bool(segments & IGNORED_DIR_NAMES)


def glossary_for_paths(paths: list[str]) -> str:
    """Monta um glossário só com as pastas de conteúdo que realmente
    aparecem no diff deste push (evita poluir o prompt com o dicionário
    inteiro toda vez)."""
    found = {}
    for path in paths:
        for seg in path.split("/"):
            key = seg.lower()
            if key in FOLDER_GLOSSARY and key not in found:
                found[key] = FOLDER_GLOSSARY[key]

    if not found:
        return "(nenhuma pasta conhecida do padrão de projeto foi alterada)"

    return "\n".join(f"- {name}/: {desc}" for name, desc in found.items())
