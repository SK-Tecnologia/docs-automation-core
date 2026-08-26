"""
Wrappers finos em torno das APIs da Anthropic (Claude) e Google (Gemini).

Mantidos com a mesma "interface" (generate(prompt) -> str) para que o
orquestrador (generate_docs.py) possa tratá-los de forma intercambiável
na hora de distribuir tarefas.
"""

import os


def estimate_tokens(text: str) -> int:
    """Estimativa grosseira (≈4 caracteres por token). Suficiente para
    balancear carga entre as duas IAs — não precisa ser exata."""
    return max(1, len(text) // 4)


class ClaudeClient:
    name = "claude"

    def __init__(self, model: str = "claude-sonnet-5"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 8000) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


class GeminiClient:
    name = "gemini"

    def __init__(self, model: str = "gemini-2.5-flash"):
        from google import genai
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 8000) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


def build_clients() -> dict:
    """Instancia os clientes disponíveis. Se faltar uma API key, aquela IA
    simplesmente não participa da distribuição (fallback pra outra)."""
    clients = {}
    if os.environ.get("ANTHROPIC_API_KEY"):
        clients["claude"] = ClaudeClient()
    if os.environ.get("GEMINI_API_KEY"):
        clients["gemini"] = GeminiClient()
    if not clients:
        raise RuntimeError("Nenhuma API key configurada (ANTHROPIC_API_KEY / GEMINI_API_KEY).")
    return clients
