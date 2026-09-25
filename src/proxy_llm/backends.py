from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from proxy_llm.metrics import last_token
from proxy_llm.types import Completion


class Cell(Protocol):
    def complete(self, messages: list[dict], seed: int = 0) -> Completion: ...


def last_user(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content") or "")
    return ""


def question_only(text: str) -> str:
    if "\nCaderno:" in text:
        return text.split("\nCaderno:", 1)[0].strip()
    return text.strip()


def extract_board(text: str) -> str:
    if "Caderno:" not in text:
        return ""
    return text.split("Caderno:", 1)[1].strip()


def parse_board_answer(board: str) -> str | None:
    if not board or board.strip() in {"", "(vazio)"}:
        return None
    parts = [p.strip() for p in board.split("|") if p.strip() and p.strip() != "(vazio)"]
    if not parts:
        return None
    from collections import Counter

    winner, _ = Counter(parts).most_common(1)[0]
    return winner


def lookup_gold(gold: dict[str, str], q: str) -> str | None:
    if q in gold:
        return gold[q]
    for k, v in gold.items():
        if k == q or k in q:
            return v
    return None


def neighbor(gold: str, salt: int = 0) -> str:
    if gold.isdigit():
        return str(int(gold) + 1 + (salt % 2))
    if gold in {"A", "B", "C"}:
        opts = [x for x in "ABC" if x != gold]
        return opts[salt % len(opts)]
    return gold + "x"


def _h(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


class HonestMockBarato:
    """Célula fraca com regime por item. Lê o caderno. Não recita «não sei»."""

    TOKENS = 8
    FOLLOW_P = 7

    def __init__(
        self,
        gold: dict[str, str] | None = None,
        regimes: dict[str, str] | None = None,
    ) -> None:
        self.gold = gold or {}
        self.regimes = regimes or {}

    def complete(self, messages: list[dict], seed: int = 0) -> Completion:
        raw = last_user(messages)
        q = question_only(raw)
        board_ans = parse_board_answer(extract_board(raw))
        if board_ans and self._follow(q, seed):
            text = board_ans
        else:
            text = self._own(q, seed)
        return Completion(text=text, tokens=self.TOKENS)

    def _follow(self, q: str, seed: int) -> bool:
        return _h(f"follow|{q}|{seed}") % 10 < self.FOLLOW_P

    def _own(self, q: str, seed: int) -> str:
        gold = lookup_gold(self.gold, q) or ""
        regime = self.regimes.get(q, "noisy")
        if not gold:
            return str(_h(f"{q}|{seed}") % 100)
        if regime == "easy":
            return gold
        if regime == "flip":
            return gold if seed % 2 == 1 else neighbor(gold)
        if regime == "stuck":
            return neighbor(gold)
        h = _h(f"{q}|{seed}")
        return gold if h % 10 < 3 else neighbor(gold, salt=h)


class MockCaro:
    """Oráculo do gabarito. Só vale como «caro» no mock; no paper, um modelo maior."""

    TOKENS = 64

    def __init__(self, gold: dict[str, str] | None = None) -> None:
        self.gold = gold or {}

    def complete(self, messages: list[dict], seed: int = 0) -> Completion:
        q = question_only(last_user(messages))
        text = lookup_gold(self.gold, q) or "?"
        return Completion(text=text, tokens=self.TOKENS, logprob=0.0)


class MLXCell:
    """SLM local. Só carrega se mlx_lm estiver instalado."""

    def __init__(self, model_id: str) -> None:
        try:
            from mlx_lm import generate, load
        except ImportError as exc:
            raise RuntimeError("pip install 'proxy-llm-inteligente[mlx]'") from exc
        self.model, self.tokenizer = load(model_id)
        self._generate = generate

    def complete(self, messages: list[dict], seed: int = 0) -> Completion:
        prompt = _messages_to_prompt(messages)
        temp = 0.15 if seed == 0 else min(0.2 + 0.1 * (seed % 6), 0.9)
        out = self._generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=32,
            temp=max(temp, 1e-5),
            verbose=False,
        )
        text = last_token(str(out).strip().splitlines()[0] if str(out).strip() else "")
        tokens = max(8, len(str(out).split()))
        return Completion(text=text, tokens=tokens)


class HttpCell:
    """Cliente OpenAI-compatível. Chave só no ambiente."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def complete(self, messages: list[dict], seed: int = 0) -> Completion:
        body = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2 if seed == 0 else 0.7,
            }
        ).encode()
        req = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"caro HTTP falhou: {exc}") from exc
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        tokens = int(usage.get("total_tokens") or (len(text.split()) + 16))
        return Completion(text=last_token(text), tokens=tokens)


def _messages_to_prompt(messages: list[dict]) -> str:
    lines = [f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages]
    lines.append("assistant:")
    return "\n".join(lines)


def make_cells(
    backend: str,
    tasks: list[dict],
    model_id: str | None = None,
    caro: str = "mock",
) -> tuple[Cell, Cell]:
    gold = {t["q"]: t["gold"] for t in tasks}
    regimes = {t["q"]: t.get("mock_regime", "noisy") for t in tasks}
    if backend == "mock":
        barato: Cell = HonestMockBarato(gold, regimes)
    elif backend == "mlx":
        barato = MLXCell(model_id or "mlx-community/Qwen2.5-0.5B-Instruct-4bit")
    else:
        raise ValueError(f"backend desconhecido: {backend}")

    if caro == "openai":
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("OPENAI_API_KEY vazia; caro=openai precisa da chave no .env")
        caro_cell: Cell = HttpCell(
            os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            key,
            os.environ.get("PROXY_CARO_MODEL", "gpt-4o-mini"),
        )
    else:
        caro_cell = MockCaro(gold)
    return barato, caro_cell


# Compatível com o teste antigo: insegurança operacional agora vive em uncertainty.py
_NAO_SEI = re.compile(r"^(não sei|nao sei|n/a|\?)$", re.IGNORECASE)


def insecure(answer: str) -> bool:
    a = (answer or "").strip()
    if not a or _NAO_SEI.match(a):
        return True
    return False
