from __future__ import annotations

from proxy_llm.metrics import normalize
from proxy_llm.types import Completion

LOGPROB_TAU = -1.2


def empty(text: str) -> bool:
    return not (text or "").strip()


def disagree(a: str, b: str) -> bool:
    if empty(a) or empty(b):
        return True
    return normalize(a) != normalize(b)


def insecure(first: Completion, second: Completion | None = None) -> bool:
    """Incerteza operacional: desacordo ou logprob baixo. Não é a string «não sei»."""
    if empty(first.text):
        return True
    if second is not None:
        return disagree(first.text, second.text)
    if first.logprob is not None:
        return first.logprob < LOGPROB_TAU
    return False
