from proxy_llm.judge import prompt_score, routellm_pick


def test_h1_comprimento_fica_no_curto_dificil(door):
    q = "Lados do hexágono?"
    assert len(q) < 80
    out = door.route([{"role": "user", "content": q}], policy="comprimento")
    assert out["route"] == "barato"


def test_h1_comprimento_gasta_no_longo_facil(door, tasks):
    q = next(t["q"] for t in tasks if t["id"] == "el01")
    assert len(q) >= 80
    out = door.route([{"role": "user", "content": q}], policy="comprimento")
    assert out["route"] == "caro"
    assert out["answer"] == "4"


def test_frugalgpt_sobe_quando_discorda(door):
    out = door.route(
        [{"role": "user", "content": "Qual a capital do Japão?"}],
        policy="frugalgpt",
    )
    assert out["route"] == "caro"
    assert out["answer"] == "Tóquio"


def test_frugalgpt_fica_no_stuck(door):
    out = door.route(
        [{"role": "user", "content": "Símbolo da água?"}],
        policy="frugalgpt",
    )
    assert out["route"] == "barato"
    assert out["answer"] != "H2O"


def test_routellm_so_superficie():
    assert prompt_score("Quanto é 2 + 2?") < 0.4
    assert routellm_pick("Quanto é 2 + 2?", 0.4) == "barato"
    assert prompt_score("17+28?") >= 0.4
    assert routellm_pick("17+28?", 0.4) == "caro"
    assert routellm_pick("Capital do Japão?", 0.4) == "barato"


def test_voto_nunca_chama_caro(door):
    out = door.route([{"role": "user", "content": "Qual a capital do Japão?"}], policy="voto")
    assert out["route"] == "voto"
    assert out["tokens"] > 0


def test_cheiro_no_flip_nao_fica_barato(door):
    out = door.route(
        [{"role": "user", "content": "Qual a capital do Japão?"}],
        policy="cheiro",
    )
    assert out["route"] in {"cheiro", "caro"}
    assert out["tokens"] > 0


def test_sempre_caro_e_oraculo(door):
    out = door.route([{"role": "user", "content": "Lados do hexágono?"}], policy="sempre_caro")
    assert out["route"] == "caro"
    assert out["answer"] == "6"
