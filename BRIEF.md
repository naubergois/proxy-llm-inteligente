# Brief

## Título

**PT:** Porteiro com cheiro: um proxy que roteia SLMs por estigmergia, não por tamanho do prompt

**EN:** A Scented Doorman: Routing Small Language Models by Stigmergy, Not Prompt Length

## Pergunta

Sob o mesmo teto de token, um proxy OpenAI-compatível que escolhe entre célula barata, enxame com caderno que evapora e um modelo caro **só no fallback** acerta mais do que (a) sempre barato, (b) sempre caro, (c) barato-se-curto?

## Hipóteses

- H1: o roteador por comprimento do prompt desperdiça token no fácil e erra o difícil que veio curto.
- H2: cache + fallback já batem o sempre-caro em custo, sem ganhar acerto.
- H3: o enxame com caderno que some, disparado só quando a célula barata está insegura, sobe o acerto sem ir ao caro na maioria das perguntas.

## O que o proxy faz (produto)

Uma API `/v1/chat/completions`. O cliente manda `model: auto`. O porteiro devolve a resposta e um cabeçalho de rota (`barato` | `cheiro` | `caro` | `cache`).

## Limite

Um Mac, um SLM local opcional, tarefas com gabarito. Não é OpenRouter. Não é Avengers com dez modelos de 7B.
