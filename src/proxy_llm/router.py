from __future__ import annotations

from collections import Counter

from proxy_llm.backends import Cell, MockCaro, last_user, make_cells
from proxy_llm.board import EvaporatingBoard
from proxy_llm.cache import ResponseCache
from proxy_llm.config import load_preregister, load_tasks
from proxy_llm.judge import prompt_score, routellm_pick
from proxy_llm.metrics import normalize
from proxy_llm.types import RouteOut
from proxy_llm.uncertainty import insecure


class Doorman:
    def __init__(
        self,
        n: int | None = None,
        half_life: int | None = None,
        barato: Cell | None = None,
        caro: Cell | None = None,
        tasks: list[dict] | None = None,
        use_cache: bool = True,
        cfg: dict | None = None,
    ) -> None:
        pre = cfg or load_preregister()
        self.n = int(n if n is not None else pre["n"])
        self.half_life = int(half_life if half_life is not None else pre["half_life"])
        self.tau = float(pre.get("tau", 1.0))
        self.length_cutoff = int(pre.get("length_cutoff", 80))
        self.routellm_threshold = float(pre.get("routellm_threshold", 0.4))
        self.token_cap = int(pre.get("token_cap", 256))
        self.probe_seeds = list(pre.get("probe_seeds", [0, 1]))
        self.scent_seeds = list(pre.get("scent_seeds", [10, 11, 12]))[: self.n]
        self.vote_seeds = list(pre.get("vote_seeds", [10, 11, 12]))[: self.n]
        self.use_cache = use_cache
        self.cache = ResponseCache()
        self.tasks = tasks if tasks is not None else load_tasks()
        if barato is None or caro is None:
            built_b, built_c = make_cells("mock", self.tasks)
            self.barato = barato or built_b
            self.caro = caro or built_c
        else:
            self.barato = barato
            self.caro = caro

    def route(self, messages: list[dict], policy: str = "cheiro") -> dict:
        user = last_user(messages)
        if policy == "auto":
            policy = "cheiro"
        if policy == "sempre_barato":
            c = self.barato.complete(messages, seed=0)
            return RouteOut(c.text, "barato", c.tokens).as_dict()
        if policy == "sempre_caro":
            c = self.caro.complete(messages, seed=0)
            return RouteOut(c.text, "caro", c.tokens).as_dict()
        if policy == "comprimento":
            dest = "barato" if len(user) < self.length_cutoff else "caro"
            backend = self.barato if dest == "barato" else self.caro
            c = backend.complete(messages, seed=0)
            return RouteOut(c.text, dest, c.tokens).as_dict()
        if policy == "routellm":
            dest = routellm_pick(user, self.routellm_threshold)
            backend = self.barato if dest == "barato" else self.caro
            c = backend.complete(messages, seed=0)
            return RouteOut(
                c.text, dest, c.tokens, {"score": prompt_score(user)}
            ).as_dict()
        if policy == "frugalgpt":
            return self._frugal(messages)
        if policy == "voto":
            return self._vote(messages)
        if policy == "cheiro":
            return self._cheiro(messages, user)
        raise ValueError(f"política desconhecida: {policy}")

    def _frugal(self, messages: list[dict]) -> dict:
        c0 = self.barato.complete(messages, seed=self.probe_seeds[0])
        c1 = self.barato.complete(messages, seed=self.probe_seeds[1])
        tokens = c0.tokens + c1.tokens
        if not insecure(c0, c1):
            return RouteOut(c0.text, "barato", tokens).as_dict()
        last = self.caro.complete(messages, seed=0)
        return RouteOut(last.text, "caro", tokens + last.tokens).as_dict()

    def _vote(self, messages: list[dict]) -> dict:
        answers: list[str] = []
        tokens = 0
        for seed in self.vote_seeds:
            c = self.barato.complete(messages, seed=seed)
            answers.append(c.text)
            tokens += c.tokens
        winner, _ = Counter(normalize(a) or a for a in answers).most_common(1)[0]
        raw = next((a for a in answers if normalize(a) == winner), answers[0])
        return RouteOut(raw, "voto", tokens).as_dict()

    def _cheiro(self, messages: list[dict], user: str) -> dict:
        if self.use_cache:
            cached = self.cache.get(user)
            if cached is not None:
                return RouteOut(cached, "cache", 0).as_dict()

        c0 = self.barato.complete(messages, seed=self.probe_seeds[0])
        c1 = self.barato.complete(messages, seed=self.probe_seeds[1])
        tokens = c0.tokens + c1.tokens
        if not insecure(c0, c1):
            self.cache.put(user, c0.text)
            return RouteOut(c0.text, "barato", tokens).as_dict()

        board = EvaporatingBoard(half_life=self.half_life)
        for seed in self.scent_seeds:
            extra = [
                {
                    "role": "user",
                    "content": f"{user}\nCaderno: {board.read() or '(vazio)'}",
                }
            ]
            c = self.barato.complete(extra, seed=seed)
            tokens += c.tokens
            board.write(c.text)
            board.tick()

        winner, frac = board.consensus()
        if winner and frac >= self.tau:
            self.cache.put(user, winner)
            return RouteOut(winner, "cheiro", tokens, {"board_frac": frac}).as_dict()

        caro_guess = 64
        if isinstance(self.caro, MockCaro):
            caro_guess = MockCaro.TOKENS
        if tokens + caro_guess > self.token_cap:
            fallback = winner or c0.text
            self.cache.put(user, fallback)
            return RouteOut(fallback, "cheiro", tokens, {"board_frac": frac}).as_dict()

        last = self.caro.complete(messages, seed=0)
        self.cache.put(user, last.text)
        return RouteOut(last.text, "caro", tokens + last.tokens, {"board_frac": frac}).as_dict()


def default_doorman() -> Doorman:
    tasks = load_tasks()
    barato, caro = make_cells("mock", tasks)
    return Doorman(barato=barato, caro=caro, tasks=tasks)
