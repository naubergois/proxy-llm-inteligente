from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from proxy_llm.metrics import normalize


@dataclass
class Trace:
    text: str
    age: int = 0


@dataclass
class EvaporatingBoard:
    """Caderno compartilhado. Meia-vida em turnos: rastro some depois de `half_life`."""

    half_life: int = 3
    traces: list[Trace] = field(default_factory=list)

    def live(self) -> list[str]:
        return [t.text for t in self.traces if t.age < self.half_life]

    def read(self) -> str:
        return " | ".join(self.live())

    def write(self, text: str) -> None:
        cleaned = " ".join(text.split())[:160]
        if cleaned:
            self.traces.append(Trace(text=cleaned, age=0))

    def tick(self) -> None:
        for t in self.traces:
            t.age += 1
        self.traces = [t for t in self.traces if t.age < self.half_life]

    def consensus(self) -> tuple[str | None, float]:
        live = self.live()
        if not live:
            return None, 0.0
        groups: dict[str, list[str]] = {}
        for t in live:
            groups.setdefault(normalize(t), []).append(t)
        best = max(groups.values(), key=len)
        return best[0], len(best) / len(live)
