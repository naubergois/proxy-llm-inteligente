from proxy_llm.router import Doorman


def test_cache_segunda_vez():
    d = Doorman()
    msgs = [{"role": "user", "content": "Quanto é 2 + 2?"}]
    a = d.route(msgs)
    b = d.route(msgs)
    assert a["route"] == "barato"
    assert b["route"] == "cache"
    assert a["answer"] == b["answer"] == "4"


def test_auto_sobe_quando_barato_hesita():
    d = Doorman()
    out = d.route([{"role": "user", "content": "Qual a capital do Japão?"}])
    assert out["route"] in {"cheiro", "caro"}
    assert "tóquio" in out["answer"].lower() or "toquio" in out["answer"].lower()
