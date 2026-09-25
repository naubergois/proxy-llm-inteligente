# Proxy inteligente para LLMs

O app fala com uma porta só. Por baixo, o porteiro escolhe: uma célula barata, um enxame que lê um caderno que some, ou o modelo caro. A pergunta da pesquisa não é se existe um proxy — LiteLLM já existe. É se o rastro que evapora muda o acerto ou o gasto de um jeito que RouteLLM e FrugalGPT não cobrem.

RouteLLM olha o texto e escolhe antes de gerar. FrugalGPT gera, vê se duas tentativas discordam, e sobe. O cheiro faz outra coisa: as células escrevem no caderno; o que ainda não evaporou decide ficar ou chamar o caro. Isso ainda não é um ChatGPT novo. É a regra no meio do caminho.

## Subir a porta

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m proxy_llm.server
```

```bash
curl -s http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto","messages":[{"role":"user","content":"Quanto é 2+2?"}]}'
```

O backend padrão é `mock`. Ele fia o protocolo. Reivindicação de paper pede `pip install -e ".[mlx]"` e `--backend mlx`, ou uma chave no `.env`. Nunca no git.

## Medir

```bash
python -m proxy_llm.bench --no-cache
python -m proxy_llm.plot
```

Sete políticas, 22 itens, acerto e token por faixa. Pré-registro em `experiments/preregister.json`. Rascunho v0.1 em `paper/article.md`. Alvo sem taxa: TMLR, lista em `VENUES.md`.
