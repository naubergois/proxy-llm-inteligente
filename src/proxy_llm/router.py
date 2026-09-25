from __future__ import annotations

from collections import Counter

from proxy_llm.backends import MockBarato, MockCaro, insecure
from proxy_llm.board import EvaporatingBoard
from proxy_llm.cache import ResponseCache


class Doorman:
    def __init__(self, n: int = 3, half_life: int = 2) -> None:
        self.n = n
        self.half_life = half_life
        self.cache = ResponseCache()
        self.barato = MockBarato()
        self.caro = MockCaro()

    def route(self, messages: list[dict], policy: str = "auto") -> dict:
        user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        if policy == "sempre_barato":
            ans = self.barato.complete(messages)
            return {"answer": ans, "route": "barato"}
        if policy == "sempre_caro":
            return {"answer": self.caro.complete(messages), "route": "caro"}
        if policy == "comprimento":
            route = "barato" if len(user) < 80 else "caro"
            backend = self.barato if route == "barato" else self.caro
            return {"answer": backend.complete(messages), "route": route}

        cached = self.cache.get(user)
        if cached is not None:
            return {"answer": cached, "route": "cache"}

        first = self.barato.complete(messages)
        if not insecure(first):
            self.cache.put(user, first)
            return {"answer": first, "route": "barato"}

        scent_ans = self._scent(messages)
        if not insecure(scent_ans):
            self.cache.put(user, scent_ans)
            return {"answer": scent_ans, "route": "cheiro"}

        last = self.caro.complete(messages)
        self.cache.put(user, last)
        return {"answer": last, "route": "caro"}

    def _scent(self, messages: list[dict]) -> str:
        board = EvaporatingBoard(half_life=self.half_life)
        answers: list[str] = []
        user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        for _ in range(self.n):
            extra = [{"role": "user", "content": f"{user}\nCaderno: {board.read() or '(vazio)'}"}]
            ans = self.barato.complete(extra)
            answers.append(ans)
            board.write(ans)
            board.tick()
        if not answers:
            return "não sei"
        winner, n = Counter(answers).most_common(1)[0]
        if insecure(winner) or n == 1:
            return "não sei"
        return winner
