from __future__ import annotations

import hashlib
import re


def _last_user(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content") or "")
    return ""


class MockBarato:
    """Célula fraca: erra o difícil e hesita no médio."""

    def complete(self, messages: list[dict]) -> str:
        q = _last_user(messages)
        if re.search(r"2\s*\+\s*2", q):
            return "4"
        if "capital do Japão" in q or "Toquio" in q or "Tóquio" in q:
            return "não sei"
        h = int(hashlib.sha256(q.encode()).hexdigest(), 16)
        if "hexágono" in q or "hexagono" in q:
            return "5" if h % 2 == 0 else "6"
        return "não sei"


class MockCaro:
    """Gerador fiel ao gabarito conhecido. Só para baseline e fallback."""

    GOLD = {
        "2+2": "4",
        "2 + 2": "4",
        "hexágono": "6",
        "hexagono": "6",
        "Japão": "Tóquio",
        "Japao": "Tóquio",
        "água": "H2O",
        "agua": "H2O",
    }

    def complete(self, messages: list[dict]) -> str:
        q = _last_user(messages)
        for k, v in self.GOLD.items():
            if k.lower() in q.lower():
                return v
        return "4"


def insecure(answer: str) -> bool:
    a = answer.strip().lower()
    if not a or a in {"não sei", "nao sei", "n/a", "?"}:
        return True
    return len(a) < 1
