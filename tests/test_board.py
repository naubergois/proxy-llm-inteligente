from proxy_llm.board import EvaporatingBoard


def test_evaporation():
    b = EvaporatingBoard(half_life=2)
    b.write("pista-boa")
    assert "pista-boa" in b.read()
    b.tick()
    assert "pista-boa" in b.read()
    b.tick()
    assert b.read() == ""


def test_half_life_n_deixa_dois_vivos():
    b = EvaporatingBoard(half_life=3)
    for text in ("A", "B", "C"):
        b.write(text)
        b.tick()
    assert b.live() == ["B", "C"]


def test_consensus_misto_nao_e_unanime():
    b = EvaporatingBoard(half_life=3)
    b.write("5")
    b.tick()
    b.write("6")
    b.tick()
    winner, frac = b.consensus()
    assert winner in {"5", "6"}
    assert frac < 1.0
