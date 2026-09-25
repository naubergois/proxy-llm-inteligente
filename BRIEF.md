# Brief

## Título

**PT:** Porteiro com cheiro: o caderno que some como sinal de rota

**EN:** A Scented Doorman: Evaporating Traces as a Routing Signal

## Pergunta

Sob o mesmo teto de token, um proxy OpenAI-compatível que usa o caderno que evapora para decidir *ficar / juntar células / subir* acerta mais, ou gasta menos, do que RouteLLM (escolhe antes de gerar), FrugalGPT (sobe se duas amostras discordam), voto casado, e os controles sempre-barato / sempre-caro / comprimento?

## Hipóteses

- H1: o roteador por comprimento do prompt erra o difícil curto e gasta o caro no fácil longo.
- H2: FrugalGPT e RouteLLM já batem o sempre-caro em custo; isso não é a novidade.
- H3: quando o barato discorda, o caderno vivo (os rastros que ainda não sumiram) decide ficar ou subir — e isso muda acerto ou gasto de um jeito que voto e cascata não cobrem.

## O que o proxy faz (produto)

Uma API `/v1/chat/completions`. O cliente manda `model: auto`. O porteiro devolve a resposta e a rota (`barato` | `cheiro` | `caro` | `cache` | `voto`).

## Limite

Um Mac, um SLM local opcional, 22 itens com gabarito. O mock fia o protocolo. Reivindicação de paper pede MLX ou uma chamada cara de verdade. Não é OpenRouter. Não é Avengers com dez modelos de 7B.
