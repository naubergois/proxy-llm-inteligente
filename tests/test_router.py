from proxy_llm.router import Doorman


def test_cache_segunda_vez(door: Doorman):
    msgs = [{"role": "user", "content": "Quanto é 2 + 2?"}]
    a = door.route(msgs, policy="cheiro")
    b = door.route(msgs, policy="cheiro")
    assert a["route"] == "barato"
    assert b["route"] == "cache"
    assert a["answer"] == b["answer"] == "4"
    assert a["tokens"] > 0
    assert b["tokens"] == 0


def test_auto_nao_fica_barato_quando_discorda(door: Doorman):
    out = door.route([{"role": "user", "content": "Qual a capital do Japão?"}], policy="auto")
    assert out["route"] in {"cheiro", "caro"}
