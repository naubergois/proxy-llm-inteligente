from pathlib import Path


def test_faixas_de_tamanho(tasks):
    for t in tasks:
        n = len(t["q"])
        if t["band"].endswith("short"):
            assert n < 80, t["id"]
        else:
            assert n >= 80, (t["id"], n)


def test_gabarito_unico(tasks):
    ids = [t["id"] for t in tasks]
    assert len(ids) == len(set(ids))
    assert len(tasks) >= 20


def test_preregister_existe():
    p = Path(__file__).resolve().parents[1] / "experiments/preregister.json"
    assert p.exists()
