from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Completion:
    text: str
    tokens: int
    logprob: float | None = None


@dataclass(frozen=True)
class RouteOut:
    answer: str
    route: str
    tokens: int
    extra: dict | None = None

    def as_dict(self) -> dict:
        d = {"answer": self.answer, "route": self.route, "tokens": self.tokens}
        if self.extra:
            d.update(self.extra)
        return d
