from proxy_llm.backends import HonestMockBarato


def test_barato_le_caderno():
    gold = {"Lados do hexágono?": "6"}
    cell = HonestMockBarato(gold, {"Lados do hexágono?": "stuck"})
    sem = cell.complete([{"role": "user", "content": "Lados do hexágono?"}], seed=0)
    assert sem.text != "6"
    found = None
    for seed in range(30):
        com = cell.complete(
            [{"role": "user", "content": "Lados do hexágono?\nCaderno: 6"}],
            seed=seed,
        )
        if com.text == "6":
            found = seed
            break
    assert found is not None


def test_stuck_falso_confianca(door):
    q = "Símbolo da água?"
    c0 = door.barato.complete([{"role": "user", "content": q}], seed=0)
    c1 = door.barato.complete([{"role": "user", "content": q}], seed=1)
    assert c0.text == c1.text
    assert c0.text != "H2O"
