from __future__ import annotations

import hashlib


class ResponseCache:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @staticmethod
    def key(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    def get(self, text: str) -> str | None:
        return self._store.get(self.key(text))

    def put(self, text: str, answer: str) -> None:
        self._store[self.key(text)] = answer
