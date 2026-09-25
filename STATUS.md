# Estado — 25 de setembro de 2026

O experimento publicável está no repo: caderno que some como sinal de rota, medido contra RouteLLM, FrugalGPT, voto e os três controles. O mock fia. O paper ainda pede SLM.

## Rascunho v0.1 (25/09)

Texto em `paper/article.md`. Código do runner + `bench` grava `fumo.summary.json`; `plot.py` gera Figuras 1–2. Citações do artigo: RouteLLM, FrugalGPT, Hybrid-LLM, AutoMix, Grassé (1959). ArXiv 2026 sem DOI ficou fora.

## Feito

- Incerteza por desacordo, não pela string «não sei».
- Célula fraca lê o caderno e muda a resposta.
- Políticas: `sempre_barato`, `sempre_caro`, `comprimento`, `routellm`, `frugalgpt`, `voto`, `cheiro`.
- 22 itens em quatro faixas, curtos e longos.
- Custo em token por chamada. Pré-registro em `experiments/preregister.json`.
- Bench: `python -m proxy_llm.bench`. Porta `/v1/chat/completions` devolve `usage.total_tokens`.
- Backend MLX e caro HTTP opcionais.

## Primeiro fumo (mock, 25/09)

`sempre_caro 1,00` (oráculo). `frugalgpt 0,82`. `routellm 0,68`. `comprimento 0,64` — H1 aparece: difícil curto 0,20, fácil longo 1,00. `cheiro 0,50`. `voto 0,32`. No mock o caderno puxa para o primeiro rastro e o cheiro perde da cascata. Isso é fiação, não resultado.

## Não misturar

O núcleo de células do `estigmergia-slm` cabe neste runner. Um experimento, um GitHub.
