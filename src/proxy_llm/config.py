from __future__ import annotations

import json
from pathlib import Path

DEFAULTS: dict = {
    "n": 3,
    "half_life": 3,
    "tau": 1.0,
    "length_cutoff": 80,
    "routellm_threshold": 0.4,
    "token_cap": 256,
    "probe_seeds": [0, 1],
    "scent_seeds": [10, 11, 12],
    "vote_seeds": [10, 11, 12],
    "policies": [
        "sempre_barato",
        "sempre_caro",
        "comprimento",
        "routellm",
        "frugalgpt",
        "voto",
        "cheiro",
    ],
}


def _candidates(name: str) -> list[Path]:
    here = Path(__file__).resolve()
    return [
        Path("experiments") / name,
        here.parents[2] / "experiments" / name,
        Path("data") / name,
    ]


def load_preregister(path: Path | None = None) -> dict:
    cfg = dict(DEFAULTS)
    files = [path] if path else _candidates("preregister.json")
    for p in files:
        if p and p.exists():
            cfg.update(json.loads(p.read_text(encoding="utf-8")))
            break
    return cfg


def load_tasks(path: Path | None = None) -> list[dict]:
    files = [path] if path else [
        Path("data/tasks.json"),
        Path(__file__).resolve().parents[2] / "data/tasks.json",
    ]
    for p in files:
        if p and p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return []
