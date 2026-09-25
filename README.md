# Proxy inteligente para LLMs

O app não escolhe modelo. Fala com uma porta só. O porteiro decide: pergunta curta fica no modelo barato; se a resposta vier fraca, sobe; se o provedor caiu, tenta o outro; se a pergunta já passou, devolve o que estava no bolso.

A pesquisa mede se essa porta, com regra de formiga (várias células pequenas e um caderno que some), gasta menos token e acerta mais do que um roteador burro — sempre barato, ou sempre caro, ou barato-ou-caro por tamanho do texto.

Isso ainda não é um ChatGPT novo. É a regra no meio do caminho.

## Subir a porta

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m proxy_llm.server
```

Depois, no outro terminal:

```bash
curl -s http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto","messages":[{"role":"user","content":"Quanto é 2+2?"}]}'
```

O backend padrão é `mock` (fumaça). Chave de API só no `.env`, nunca no git.

## Revista sem taxa

TMLR primeiro. Lista em `VENUES.md`.
