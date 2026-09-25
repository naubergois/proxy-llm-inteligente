from __future__ import annotations

import json
from pathlib import Path

from proxy_llm.router import Doorman


def main() -> None:
    tasks = json.loads(Path("data/tasks.json").read_text(encoding="utf-8"))
    door = Doorman()
    policies = ("sempre_barato", "sempre_caro", "comprimento", "auto")
    print("politica        acerto  rotas")
    for pol in policies:
        door.cache._store.clear()
        ok = 0
        routes: dict[str, int] = {}
        for t in tasks:
            out = door.route(
                [{"role": "user", "content": t["q"]}],
                policy=pol,
            )
            gold = t["gold"].lower()
            ans = out["answer"].lower()
            if gold in ans or ans in gold:
                ok += 1
            routes[out["route"]] = routes.get(out["route"], 0) + 1
        print(f"{pol:14} {ok / len(tasks):.2f}   {routes}")


if __name__ == "__main__":
    main()
