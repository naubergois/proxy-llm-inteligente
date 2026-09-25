from proxy_llm.metrics import correct, error_correlation, normalize
from proxy_llm.types import Completion
from proxy_llm.uncertainty import disagree, insecure


def test_incerteza_e_desacordo_nao_string(door):
    q = "Qual a capital do Japão?"
    c0 = door.barato.complete([{"role": "user", "content": q}], seed=0)
    c1 = door.barato.complete([{"role": "user", "content": q}], seed=1)
    assert c0.text.lower() not in {"não sei", "nao sei"}
    assert c1.text.lower() not in {"não sei", "nao sei"}
    assert normalize(c0.text) != normalize(c1.text)
    assert insecure(c0, c1)


def test_easy_concorda(door):
    q = "Quanto é 2 + 2?"
    c0 = door.barato.complete([{"role": "user", "content": q}], seed=0)
    c1 = door.barato.complete([{"role": "user", "content": q}], seed=1)
    assert c0.text == c1.text == "4"
    assert not insecure(c0, c1)


def test_metrics():
    assert correct("45", "45")
    assert correct("Tóquio", "Toquio")
    assert not correct("Tóquiox", "Tóquio")
    assert error_correlation(["3", "3", "3"], "4") == 1.0
    assert error_correlation(["3", "5"], "4") == 0.0
    assert disagree("6", "5")
    _ = Completion
