from __future__ import annotations

import re

# Só superfície do prompt. Sem gabarito, sem lista de fatos.
_MATH = re.compile(r"[×÷³%]|resto", re.IGNORECASE)
_NUM = re.compile(r"\d+")


def prompt_score(q: str) -> float:
    """Juiz pré-geração no estilo RouteLLM: features do texto, uma geração depois."""
    nums = [int(x) for x in _NUM.findall(q)]
    big = sum(1 for n in nums if n >= 10)
    score = 0.0
    if len(q) >= 80:
        score += 0.3
    score += 0.25 * min(big, 2)
    if _MATH.search(q):
        score += 0.3
    if len(q.split()) >= 20:
        score += 0.2
    return min(score, 1.0)


def routellm_pick(q: str, threshold: float) -> str:
    return "caro" if prompt_score(q) >= threshold else "barato"
