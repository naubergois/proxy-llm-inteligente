from pathlib import Path

import json

from proxy_llm.bench import main
from proxy_llm.config import load_preregister


def test_bench_mock_corre(tasks, tmp_path):
    out = tmp_path / "fumo.jsonl"
    main(["--out", str(out), "--no-cache"])
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    policies = load_preregister()["policies"]
    assert len(lines) == len(policies) * len(tasks)
    summary = json.loads(out.with_suffix(".summary.json").read_text(encoding="utf-8"))
    assert summary["fixture"] is True
    assert [r["politica"] for r in summary["overall"]] == policies
