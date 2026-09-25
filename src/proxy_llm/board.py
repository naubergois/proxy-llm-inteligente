from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Trace:
    text: str
    age: int = 0


@dataclass
class EvaporatingBoard:
    half_life: int = 2
    traces: list[Trace] = field(default_factory=list)

    def read(self) -> str:
        return " | ".join(t.text for t in self.traces if t.age < self.half_life)

    def write(self, text: str) -> None:
        cleaned = " ".join(text.split())[:160]
        if cleaned:
            self.traces.append(Trace(text=cleaned))

    def tick(self) -> None:
        for t in self.traces:
            t.age += 1
        self.traces = [t for t in self.traces if t.age < self.half_life]
