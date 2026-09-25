from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Figuras do fumo a partir do summary.json")
    p.add_argument("--summary", type=Path, default=Path("results/fumo.summary.json"))
    p.add_argument("--outdir", type=Path, default=Path("paper/figures"))
    args = p.parse_args(argv)

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    args.outdir.mkdir(parents=True, exist_ok=True)
    _write_table_md(data, args.outdir / "tabela1.md")
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("pip install matplotlib") from exc
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    overall = data["overall"]
    names = [r["politica"] for r in overall]
    acc = [r["acerto"] for r in overall]
    toks = [r["tokens"] for r in overall]

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.scatter(toks, acc, s=36, c="#1f4e79", zorder=3)
    for n, x, y in zip(names, toks, acc):
        ax.annotate(n, (x, y), textcoords="offset points", xytext=(4, 4), fontsize=7)
    ax.set_xlabel("tokens (soma no conjunto)")
    ax.set_ylabel("acerto")
    ax.set_ylim(0, 1.05)
    ax.set_title("Fiação mock: não é resultado de SLM")
    fig.tight_layout()
    fig.savefig(args.outdir / "fig1_acerto_token.pdf")
    fig.savefig(args.outdir / "fig1_acerto_token.png", dpi=160)
    plt.close(fig)

    want = ("comprimento", "routellm", "frugalgpt", "cheiro")
    bands = ("hard_short", "easy_long")
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    x = range(len(want))
    w = 0.35
    by = {(b["politica"], b["band"]): b["acerto"] for b in data["bands"]}
    h1 = [by.get((p, "hard_short"), 0) for p in want]
    h2 = [by.get((p, "easy_long"), 0) for p in want]
    ax.bar([i - w / 2 for i in x], h1, w, label="difícil curto", color="#7a1f1f")
    ax.bar([i + w / 2 for i in x], h2, w, label="fácil longo", color="#2f6b3a")
    ax.set_xticks(list(x))
    ax.set_xticklabels(want, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("acerto")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("H1 no mock: comprimento erra o curto difícil")
    fig.tight_layout()
    fig.savefig(args.outdir / "fig2_faixas.pdf")
    fig.savefig(args.outdir / "fig2_faixas.png", dpi=160)
    plt.close(fig)
    print(f"figuras em {args.outdir}")


def _write_table_md(data: dict, path: Path) -> None:
    lines = [
        "| política | acerto | tokens | rotas |",
        "|---|---:|---:|---|",
    ]
    for r in data["overall"]:
        rotas = ", ".join(f"{k}:{v}" for k, v in r["rotas"].items())
        lines.append(f"| {r['politica']} | {r['acerto']:.2f} | {r['tokens']} | {rotas} |")
    if data.get("fixture"):
        lines.append("")
        lines.append("*Fiação mock. O caro é oráculo. Não citar como resultado de SLM.*")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
