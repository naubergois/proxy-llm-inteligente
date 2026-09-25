# O que já existe e o que ainda falta

A porta `/v1/chat/completions` sobe. Isso ainda não é descoberta. Roteador barato/caro, cache da mesma pergunta e fallback quando o primeiro hesita já têm nome na literatura e produto na prateleira. O paper só nasce se o **cheiro** — o caderno que some — mudar o acerto ou o gasto de um jeito que RouteLLM e FrugalGPT não cobrem.

## Já publicado (não reivindicar)

**Porteiro por pergunta, antes de gerar.** RouteLLM (arXiv:2406.18665, ICLR 2025) e Hybrid-LLM (ICLR 2024) escolhem um modelo fraco ou forte olhando o texto. OpenRouter e LiteLLM fazem a porta OpenAI. Isso é o `model: auto` sem enxame.

**Cascata depois de gerar.** FrugalGPT (TMLR 2024) gera, nota a qualidade, sobe se estiver fraco. AutoMix e o survey de 2026 (arXiv:2603.04445) chamam isso de cascade. O nosso `barato → inseguro → caro` é essa escada, com a palavra “não sei” no lugar de um juiz.

**Enxame que vota.** Cognitive Cells (arXiv:2608.28606) e Avengers (AAAI 2026) já mediram voto e debate. Soma de células só ajuda se o erro não for o mesmo.

**Estigmergia sem a porta.** Emergent Culture (arXiv:2606.30668) e SwarmWorld (arXiv:2608.26081) usam o chão que some para cultura ou tecnologia. Não medem acerto versus RouteLLM. SWARM-LLM (arXiv:2606.14711) sobe para a nuvem por incerteza, sem caderno.

**Consenso pode ser sorte.** arXiv:2603.24676. Se o cheiro vira voto da mesma string, o paper de deriva já avisou.

## O que este repo ainda encena

O `bench` de ontem deu `auto = 1,00` e `sempre_caro = 1,00`. O caro conhece o gabarito de cor. O barato diz “não sei” nas perguntas que combinamos. Cinco itens, todos curtos: o baseline de comprimento **nunca** chama o caro. O caderno é escrito, mas o mock **não lê** o rastro para mudar a conta — só olha palavra-chave. Incerteza é a string “não sei”, não logprob. Sem SLM, H1–H3 são roteiro.

## O que ainda dá para melhorar (e publicar)

1. **O cheiro como sinal de rota, não como metáfora.** Ninguém no survey de roteamento evapora um quadro compartilhado para decidir *ficar / enxame / subir*. Cognitive Cells testou voto e debate, não evaporação. Essa é a fatia.

2. **Baseline que já existe, não o de comprimento.** Comparar com: sempre barato, sempre caro, FrugalGPT (cascata por qualidade), RouteLLM ou um juiz pequeno, e voto casado em token (Cognitive Cells). Comprimento do prompt fica como controle fraco, não como adversário.

3. **Pergunta curta e difícil.** H1 morre se toda pergunta difícil for longa. Precisa de conta curta que o 0,5B erra e o caro acerta.

4. **Incerteza de verdade.** Logprob, duas amostras que discordam, ou um classificador. Sem isso a cascata é if-not-sei.

5. **O modelo tem que ler o caderno.** Se o rastro não muda a próxima resposta, não é estigmergia. É voto com extra.

6. **Um paper, um runner.** `estigmergia-slm` mede protocolo. Este repo mede a porta. TMLR quer um experimento, não dois produtos. O proxy chama o mesmo núcleo de células.

7. **Custo em token real.** Caracteres do mock não convencem. SLM local (MLX) + uma chamada cara só no fallback.

Sem o item 1 medido em modelo de verdade, o GitHub é um LiteLLM menor. Com o item 1 e os baselines do item 2, a pergunta volta a ser borda.

## Implementado (25 de setembro de 2026)

O runner compara `cheiro` com RouteLLM, FrugalGPT, voto, comprimento, sempre-barato e sempre-caro. Incerteza é desacordo. A célula lê o caderno. Token entra no desfecho. 22 itens nas quatro faixas. O `caro` do mock continua oráculo: sem MLX ou API, o número do bench não é resultado.
