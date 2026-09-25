from __future__ import annotations

import json
from pathlib import Path

import pytest

from proxy_llm.backends import make_cells
from proxy_llm.router import Doorman

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def tasks() -> list[dict]:
    return json.loads((ROOT / "data/tasks.json").read_text(encoding="utf-8"))


@pytest.fixture
def door(tasks: list[dict]) -> Doorman:
    barato, caro = make_cells("mock", tasks)
    return Doorman(barato=barato, caro=caro, tasks=tasks)
