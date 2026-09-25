from __future__ import annotations

import unicodedata


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return "".join(ch.lower() for ch in s if ch.isalnum())


def last_token(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    lower = raw.lower()
    if "resposta:" in lower:
        return raw.split(":")[-1].strip().split()[0]
    return raw.split()[-1]


def correct(answer: str, gold: str) -> bool:
    a, g = normalize(answer), normalize(gold)
    if not g:
        return False
    if a == g:
        return True
    return normalize(last_token(answer)) == g


def error_correlation(answers: list[str], gold: str) -> float | None:
    wrong = [a for a in answers if not correct(a, gold)]
    if len(wrong) < 2:
        return None
    pairs = 0
    same = 0
    for i, left in enumerate(wrong):
        for right in wrong[i + 1 :]:
            pairs += 1
            if normalize(left) == normalize(right):
                same += 1
    return same / pairs
