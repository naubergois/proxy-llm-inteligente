from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from proxy_llm.backends import MockCaro, make_cells
from proxy_llm.config import load_preregister, load_tasks
from proxy_llm.metrics import correct
from proxy_llm.router import Doorman


def main(argv: list[str] | None = None) -> None:
    pre = load_preregister()
    p = argparse.ArgumentParser(description="Bench do porteiro: cheiro vs baselines publicados")
    p.add_argument("--backend", choices=["mock", "mlx"], default="mock")
    p.add_argument("--caro", choices=["mock", "openai"], default="mock")
    p.add_argument("--model", default=None)
    p.add_argument("--tasks", type=Path, default=None)
    p.add_argument("--out", type=Path, default=Path("results/fumo.jsonl"))
    p.add_argument("--no-cache", action="store_true")
    args = p.parse_args(argv)

    tasks = load_tasks(args.tasks)
    if not tasks:
        raise SystemExit("data/tasks.json vazio ou ausente")
    barato, caro = make_cells(args.backend, tasks, args.model, caro=args.caro)
    door = Doorman(barato=barato, caro=caro, tasks=tasks, use_cache=not args.no_cache)
    policies = list(pre.get("policies") or [])
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.backend == "mock" or isinstance(caro, MockCaro):
        print("aviso: caro=oráculo no mock. Reivindicação de paper pede SLM ou API.")

    rows: list[dict] = []
    with args.out.open("w", encoding="utf-8") as fh:
        for pol in policies:
            door.cache._store.clear()
            for t in tasks:
                out = door.route([{"role": "user", "content": t["q"]}], policy=pol)
                ok = correct(out["answer"], t["gold"])
                row = {
                    "id": t["id"],
                    "politica": pol,
                    "band": t.get("band", ""),
                    "regime": t.get("mock_regime", ""),
                    "acerto": int(ok),
                    "resposta": out["answer"],
                    "ouro": t["gold"],
                    "route": out["route"],
                    "tokens": out["tokens"],
                    "chars": len(t["q"]),
                }
                rows.append(row)
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = build_summary(rows, policies, backend=args.backend, caro=args.caro)
    summary_path = args.out.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _print_summary(rows, policies)
    _print_bands(rows, policies)


def build_summary(
    rows: list[dict],
    policies: list[str],
    backend: str = "mock",
    caro: str = "mock",
) -> dict:
    overall = []
    bands_out = []
    band_names = ("easy_short", "easy_long", "hard_short", "hard_long")
    for pol in policies:
        chunk = [r for r in rows if r["politica"] == pol]
        if not chunk:
            continue
        routes: dict[str, int] = defaultdict(int)
        for r in chunk:
            routes[r["route"]] += 1
        overall.append(
            {
                "politica": pol,
                "n": len(chunk),
                "acerto": sum(r["acerto"] for r in chunk) / len(chunk),
                "tokens": sum(r["tokens"] for r in chunk),
                "rotas": dict(routes),
            }
        )
        for band in band_names:
            sub = [r for r in chunk if r["band"] == band]
            if not sub:
                continue
            bands_out.append(
                {
                    "politica": pol,
                    "band": band,
                    "n": len(sub),
                    "acerto": sum(r["acerto"] for r in sub) / len(sub),
                }
            )
    return {
        "backend": backend,
        "caro": caro,
        "fixture": backend == "mock" or caro == "mock",
        "overall": overall,
        "bands": bands_out,
    }


def _print_summary(rows: list[dict], policies: list[str]) -> None:
    print("politica        acerto  tokens  rotas")
    for pol in policies:
        chunk = [r for r in rows if r["politica"] == pol]
        if not chunk:
            continue
        acc = sum(r["acerto"] for r in chunk) / len(chunk)
        toks = sum(r["tokens"] for r in chunk)
        routes: dict[str, int] = defaultdict(int)
        for r in chunk:
            routes[r["route"]] += 1
        print(f"{pol:14} {acc:.2f}    {toks:5}  {dict(routes)}")


def _print_bands(rows: list[dict], policies: list[str]) -> None:
    print("politica        faixa        acerto")
    bands = ("easy_short", "easy_long", "hard_short", "hard_long")
    for pol in policies:
        for band in bands:
            chunk = [r for r in rows if r["politica"] == pol and r["band"] == band]
            if not chunk:
                continue
            acc = sum(r["acerto"] for r in chunk) / len(chunk)
            print(f"{pol:14} {band:12} {acc:.2f}  ({len(chunk)})")


if __name__ == "__main__":
    main()
